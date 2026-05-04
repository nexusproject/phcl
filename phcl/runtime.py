"""
Python-side runtime helpers for PHCL authoring.

These helpers execute during PHCL generation/build time rather than being
rendered as HCL expressions in the output.
"""

from __future__ import annotations

import inspect
import warnings
from pathlib import Path
from string import Template

from .core.expression import Expression, hcl


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


def heredoc(value: str, marker: str = "HEREDOC_EOF") -> Expression:
    """
    Render a Python string as an indented HCL heredoc expression.

    This is useful when content already exists on the Python side and should be
    emitted as an HCL heredoc rather than a quoted string. A single trailing
    newline is trimmed before wrapping so content loaded from files via
    ``read_text()`` does not accidentally gain an extra blank line.
    """

    return _heredoc(value, marker=marker)


def multiline(value: str, marker: str = "MULTILINE_EOF") -> Expression:
    warnings.warn(
        "`multiline(...)` is deprecated and will be removed in a future "
        "release; use `heredoc(...)` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return heredoc(value, marker=marker)


def render_file(
    path: str | Path,
    *,
    context: dict[str, object] | None = None,
    heredoc: bool | None = None,
    multiline: bool | None = None,
    marker: str = "HEREDOC_EOF",
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
        if marker == "HEREDOC_EOF":
            marker = "MULTILINE_EOF"

    heredoc = True if heredoc is None else heredoc

    if heredoc:
        return _heredoc(rendered, marker=marker)
    return rendered


__all__ = ["path_module", "heredoc", "multiline", "render_file"]
