"""
Curated authoring surface for everyday PHCL use.

`phcl.syntax` is meant to be the place you reach for when writing PHCL code,
without having to remember which helper is technically a decorator, a block
alias, or an expression helper.
"""

from .core import Block as B
from .core.decorators import abstract, generate
from .core.expression import hcl, jsonencode

__all__ = [
    "B",
    "abstract",
    "generate",
    "hcl",
    "jsonencode",
]
