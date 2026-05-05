"""
Python-side runtime helpers for PHCL authoring.

These helpers execute during PHCL generation/build time rather than being
rendered as HCL expressions in the output.
"""

from __future__ import annotations

import inspect
import json
import keyword
import os
import warnings
from collections.abc import Mapping
from pathlib import Path
from string import Template
from typing import Any, Union

from .core import Block
from .core.expression import Expression, hcl


_PathLike = Union[str, os.PathLike[str]]
_Selector = Union[str, list[str], tuple[str, ...]]


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


def dict_block(data: Mapping[str, Any]) -> type[Block]:
    if not isinstance(data, Mapping):
        raise TypeError("dict_block(...) expects a mapping")

    attrs = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise TypeError("dict_block(...) keys must be strings")
        if not key.isidentifier() or keyword.iskeyword(key):
            raise ValueError("dict_block(...) keys must be valid Python identifiers")
        if key.startswith("_"):
            raise ValueError("Attributes starting with '_' are reserved")
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


def _select_mapping(data: Any, *, at: _Selector | None, source: Path) -> Mapping[str, Any]:
    selected = data
    if at is not None:
        path = [at] if isinstance(at, str) else list(at)
        for key in path:
            if not isinstance(selected, Mapping):
                raise TypeError(
                    f"{source} selection at {key!r} cannot continue through "
                    f"{type(selected).__name__}"
                )
            try:
                selected = selected[key]
            except KeyError as exc:
                raise KeyError(f"{source} does not contain mapping key {key!r}") from exc

    if not isinstance(selected, Mapping):
        location = "root" if at is None else f"selection {at!r}"
        raise TypeError(f"{source} {location} must be a mapping")

    return selected


def json_block(path: _PathLike, *, at: _Selector | None = None) -> type[Block]:
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    return dict_block(_select_mapping(data, at=at, source=source))


def yaml_block(path: _PathLike, *, at: _Selector | None = None) -> type[Block]:
    from ruamel.yaml import YAML

    source = Path(path)
    data = YAML(typ="safe").load(source.read_text(encoding="utf-8"))
    return dict_block(_select_mapping(data, at=at, source=source))


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
    "heredoc",
    "multiline",
    "dict_block",
    "json_block",
    "yaml_block",
    "block_dict",
    "render_file",
]
