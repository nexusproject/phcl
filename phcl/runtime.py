"""
Python-side runtime helpers for PHCL authoring.

These helpers execute during PHCL generation/build time rather than being
rendered as HCL expressions in the output.
"""

from __future__ import annotations

import inspect
import json
import os
import re
import warnings
from collections.abc import Mapping
from contextvars import ContextVar, Token
from pathlib import Path
from string import Template
from typing import Any, Optional, Union

from .core import Block
from .core.nodes import class_to_label
from .core.expression import Expression, hcl


_PathLike = Union[str, os.PathLike[str]]
_Selector = Union[str, list[str], tuple[str, ...]]
_BUILD_TARGET: ContextVar[Optional[Path]] = ContextVar(
    "phcl_build_target",
    default=None,
)
_GENERATION_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_MAX_ERROR_REPR = 80


def _set_build_target(path: Path) -> Token[Optional[Path]]:
    return _BUILD_TARGET.set(path.resolve())


def _reset_build_target(token: Token[Optional[Path]]) -> None:
    _BUILD_TARGET.reset(token)


def path_module() -> Path:
    """
    Return the directory of the calling PHCL source module as a ``Path``.

    This is a Python-side runtime helper analogous in spirit to Terraform's
    ``path.module``, but it resolves against the caller's source file during
    PHCL generation.
    """

    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        raise RuntimeError("path_module() could not resolve the calling frame")

    caller_globals = frame.f_back.f_globals
    caller_file = caller_globals.get("__file__")
    if not caller_file:
        raise RuntimeError("path_module() requires the calling module to define __file__")

    return Path(caller_file).resolve().parent


def path_target() -> Path:
    """
    Return the current ``phcl build <target>`` directory.

    This value is available while PHCL source files are loaded by the CLI. It
    is intentionally tied to the active build invocation, unlike
    ``path_module()`` which is tied to the current source module.
    """

    target = _BUILD_TARGET.get()
    if target is None:
        raise RuntimeError("path_target() is only available during phcl build")
    return target


def _heredoc(value: str, marker: str) -> Expression:
    body = value[:-1] if value.endswith("\n") else value
    return hcl(f"""<<-{marker}
{body}
{marker}""")


def heredoc(value: str, marker: str = "EOF") -> Expression:
    """
    Render a Python string as an indented HCL heredoc expression.

    This is useful when content already exists on the Python side and should be
    emitted as an HCL heredoc rather than a quoted string. A single trailing
    newline is trimmed before wrapping so content loaded from files via
    ``read_text()`` does not accidentally gain an extra blank line.
    """

    return _heredoc(value, marker=marker)


def multiline(value: str, marker: str = "EOF") -> Expression:
    warnings.warn(
        "`multiline(...)` is deprecated and will be removed in a future "
        "release; use `heredoc(...)` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return heredoc(value, marker=marker)


def _validate_block_attribute_name(name: Any) -> str:
    if not isinstance(name, str):
        raise TypeError(
            f"PHCL block attribute name {name!r} must be a string"
        )
    if name.startswith("-") or not name.replace("-", "_").isidentifier():
        raise ValueError(
            f"PHCL block attribute name {name!r} must be a valid HCL "
            "identifier"
        )
    if name == "_":
        raise ValueError(
            "PHCL block attribute name '_' is reserved"
        )
    if name.startswith("_phcl_"):
        raise ValueError(
            f"PHCL block attribute name {name!r} is reserved because names "
            "cannot start with '_phcl_'"
        )
    return name


def _derive_class(
    ancestor: type[Block],
    label: str,
    attrs: Mapping[str, Any],
    *,
    module_name: str,
) -> type[Block]:
    if not isinstance(ancestor, type) or not issubclass(ancestor, Block):
        raise TypeError("derive(...) expects a Block ancestor class")
    if not isinstance(label, str):
        raise TypeError("derive(...) label must be a string")
    if not label:
        raise ValueError("derive(...) label cannot be empty")

    namespace = {"__module__": module_name}
    for key, value in attrs.items():
        try:
            key = _validate_block_attribute_name(key)
        except (TypeError, ValueError) as exc:
            raise type(exc)(f"derive(...) invalid attribute: {exc}") from exc
        namespace[key] = value

    return type(label, (ancestor,), namespace)


def derive(ancestor: type[Block], label: str, **attrs: Any) -> type[Block]:
    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None
    caller_module = (
        caller.f_globals.get("__name__", ancestor.__module__)
        if caller is not None
        else ancestor.__module__
    )

    return _derive_class(ancestor, label, attrs, module_name=caller_module)


class _GenerationItem:
    def __init__(self, *, index: int, key: str, value: Any, label: str | None = None):
        self.index = index
        self.key = key
        self.value = value
        self.label = label


class _ThisExpr:
    def __init__(self, root: str, path: tuple[tuple[str, Any], ...] = ()):
        self._root = root
        self._path = path

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return _ThisExpr(self._root, self._path + (("attr", name),))

    def __getitem__(self, key: Any):
        return _ThisExpr(self._root, self._path + (("item", key),))

    def _phcl_resolve(self, item: _GenerationItem):
        value = getattr(item, self._root)
        for op, arg in self._path:
            if op == "attr":
                value = getattr(value, arg)
            else:
                value = value[arg]
        return value

    def _phcl_normalize(self):
        raise RuntimeError("`this` is only available inside `generate(...)`")


class _This:
    @property
    def index(self) -> _ThisExpr:
        return _ThisExpr("index")

    @property
    def key(self) -> _ThisExpr:
        return _ThisExpr("key")

    @property
    def value(self) -> _ThisExpr:
        return _ThisExpr("value")

    @property
    def label(self) -> _ThisExpr:
        return _ThisExpr("label")


this = _This()


def _validate_generation_key(key: Any) -> str:
    if not isinstance(key, str):
        raise TypeError("generate(...) keys must be strings")

    key_repr = repr(key)
    if len(key_repr) > _MAX_ERROR_REPR:
        key_repr = f"{key_repr[:_MAX_ERROR_REPR - 3]}..."

    if not _GENERATION_KEY_RE.match(key):
        raise ValueError(
            f"generate(...) key {key_repr} must match [A-Za-z][A-Za-z0-9_]*"
        )
    return key


def _resolve_this(value: Any, item: _GenerationItem) -> Any:
    if isinstance(value, _ThisExpr):
        return value._phcl_resolve(item)
    if isinstance(value, list):
        return [_resolve_this(item_value, item) for item_value in value]
    if isinstance(value, tuple):
        return tuple(_resolve_this(item_value, item) for item_value in value)
    if isinstance(value, Mapping):
        return {
            key: _resolve_this(item_value, item)
            for key, item_value in value.items()
        }
    return value


def _generation_items(data: Mapping[str, Any] | list[Any]) -> list[_GenerationItem]:
    if isinstance(data, Mapping):
        return [
            _GenerationItem(index=index, key=_validate_generation_key(key), value=value)
            for index, (key, value) in enumerate(data.items())
        ]

    if isinstance(data, list):
        return [
            _GenerationItem(index=index, key=str(index), value=value)
            for index, value in enumerate(data)
        ]

    raise TypeError("generate(...) expects a mapping or list")


def generate(data: Mapping[str, Any] | list[Any]):
    items = _generation_items(data)

    def decorator(cls: type[Block]) -> type[Block]:
        if not isinstance(cls, type) or not issubclass(cls, Block):
            raise TypeError("generate(...) can only decorate Block classes")
        if cls.__dict__.get("_phcl_generated_template", False):
            raise TypeError(
                "generate(...) cannot be stacked; use derive(...) for custom "
                "generation flows"
            )

        cls._phcl_abstract = True
        cls._phcl_generated_template = True
        cls._phcl_generation_classes = {}
        for item in items:
            generated_name = f"{cls.__name__}_{item.key}"
            item.label = (
                class_to_label(generated_name)
                if getattr(cls, "_phcl_auto_label", True)
                else None
            )
            attrs = {}
            for name, value in cls.__dict__.items():
                if name == "_" or name.startswith("_phcl_") or (
                    name.startswith("__") and name.endswith("__")
                ):
                    continue
                attrs[name] = _resolve_this(value, item)

            generated_cls = _derive_class(
                cls,
                generated_name,
                attrs,
                module_name=cls.__module__,
            )
            cls._phcl_generation_classes[item.key] = generated_cls

        return cls

    return decorator


def dict_block(data: Mapping[str, Any]) -> type[Block]:
    if not isinstance(data, Mapping):
        raise TypeError("dict_block(...) expects a mapping")

    attrs = {}
    for key, value in data.items():
        try:
            key = _validate_block_attribute_name(key)
        except (TypeError, ValueError) as exc:
            raise type(exc)(f"dict_block(...) invalid key: {exc}") from exc
        attrs[key] = value

    return type(
        "DictBlock",
        (Block,),
        {
            "__module__": __name__,
            "_phcl_abstract": True,
            **attrs,
        },
    )


def _normalize_selector(at: _Selector | None) -> list[str]:
    if at is None:
        return []
    if isinstance(at, str):
        return [at]
    if not isinstance(at, (list, tuple)):
        raise TypeError("at must be a string key or a list/tuple of string keys")

    path = list(at)
    if not all(isinstance(key, str) for key in path):
        raise TypeError("at must contain only string keys")
    return path


def _format_selection(path: list[str]) -> str:
    if not path:
        return "root"
    if len(path) == 1:
        return f"at={path[0]!r}"
    return f"at={tuple(path)!r}"


def _format_source(source: Path) -> str:
    resolved = source.resolve()
    target = _BUILD_TARGET.get()
    if target is not None:
        try:
            return str(resolved.relative_to(target))
        except ValueError:
            pass
    return str(source)


def _select_mapping(data: Any, *, at: _Selector | None, source: Path) -> Mapping[str, Any]:
    source_label = _format_source(source)
    selected = data
    path = _normalize_selector(at)
    visited: list[str] = []
    for key in path:
        if not isinstance(selected, Mapping):
            raise TypeError(
                f"{source_label} selection {_format_selection(visited)} cannot "
                f"continue at {key!r}; got {type(selected).__name__}"
            )
        try:
            selected = selected[key]
        except KeyError as exc:
            raise KeyError(
                f"{source_label} selection {_format_selection(visited + [key])} "
                f"does not exist"
            ) from exc
        visited.append(key)

    if not isinstance(selected, Mapping):
        raise TypeError(
            f"{source_label} selection {_format_selection(path)} must be a mapping; "
            f"got {type(selected).__name__}"
        )

    return selected


def _file_block(data: Any, *, at: _Selector | None, source: Path) -> type[Block]:
    selected = _select_mapping(data, at=at, source=source)
    try:
        return dict_block(selected)
    except (TypeError, ValueError) as exc:
        raise type(exc)(
            f"{_format_source(source)} selection {_format_selection(_normalize_selector(at))} "
            f"contains invalid PHCL block attributes: {exc}"
        ) from exc


def json_block(path: _PathLike, *, at: _Selector | None = None) -> type[Block]:
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    return _file_block(data, at=at, source=source)


def yaml_block(path: _PathLike, *, at: _Selector | None = None) -> type[Block]:
    from ruamel.yaml import YAML

    source = Path(path)
    data = YAML(typ="safe").load(source.read_text(encoding="utf-8"))
    return _file_block(data, at=at, source=source)


def block_dict(block: Block | type[Block]) -> dict[str, Any]:
    if isinstance(block, type) and issubclass(block, Block):
        block = block()

    if not isinstance(block, Block):
        raise TypeError("block_dict(...) expects a Block instance or Block class")

    return dict(block._phcl_attributes)


def render_file(
    path: str | Path,
    *,
    context: dict[str, object] | None = None,
    heredoc: bool | None = None,
    multiline: bool | None = None,
    marker: str = "EOF",
    encoding: str = "utf-8",
) -> str | Expression:
    """
    Read a file, optionally apply ``string.Template`` substitution, and return
    either the rendered text or an HCL heredoc expression.
    """

    rendered = Path(path).read_text(encoding=encoding)
    if context:
        rendered = Template(rendered).substitute(context)

    if heredoc is not None and multiline is not None:
        raise ValueError("render_file() cannot use both heredoc and multiline")

    if multiline is not None:
        warnings.warn(
            "`render_file(..., multiline=...)` is deprecated and will be "
            "removed in a future release; use `heredoc=...` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        heredoc = multiline
    heredoc = True if heredoc is None else heredoc

    if heredoc:
        return _heredoc(rendered, marker=marker)
    return rendered


__all__ = [
    "path_module",
    "path_target",
    "heredoc",
    "multiline",
    "derive",
    "generate",
    "this",
    "dict_block",
    "json_block",
    "yaml_block",
    "block_dict",
    "render_file",
]
