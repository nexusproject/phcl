from typing import Any, Dict, List, Type

from ..core.dsl import Node
from ..core.elements import Addressable


def abstract(cls: Type[Node]) -> Type[Node]:
    """Marks Node class as non-renderable."""
    cls._phcl_abstract = True
    return cls


def label(value: str):
    """Define custom terraform label."""
    def deco(cls: Type[Addressable]) -> Type[Addressable]:
        cls._phcl_label = value
        return cls
    return deco