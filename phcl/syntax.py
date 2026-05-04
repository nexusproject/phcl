"""
Curated authoring surface for everyday PHCL use.

`phcl.syntax` is meant to be the place you reach for when writing PHCL code,
without having to remember which helper is technically a decorator, a block
alias, or an expression helper.
"""

from __future__ import annotations

import warnings

from .core import Block as B
from .core.decorators import abstract, generate
from .core.expression import Expression, _HCLValue, hcl, hcl_call


def hcl_jsonencode(value: _HCLValue) -> Expression:
    return hcl_call("jsonencode", value)


def hcl_yamlencode(value: _HCLValue) -> Expression:
    return hcl_call("yamlencode", value)


def hcl_file(path: str | Expression) -> Expression:
    return hcl_call("file", path)


def hcl_templatefile(path: str | Expression, vars: _HCLValue) -> Expression:
    return hcl_call("templatefile", path, vars)


def jsonencode(value: _HCLValue) -> Expression:
    warnings.warn(
        "`jsonencode(...)` is deprecated and will be removed in a future "
        "release; use `hcl_jsonencode(...)` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return hcl_jsonencode(value)


def file(path: str | Expression) -> Expression:
    warnings.warn(
        "`file(...)` is deprecated and will be removed in a future release; "
        "use `hcl_file(...)` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return hcl_file(path)

__all__ = [
    "B",
    "abstract",
    "generate",
    "hcl",
    "hcl_call",
    "hcl_file",
    "hcl_jsonencode",
    "hcl_templatefile",
    "hcl_yamlencode",
]
