from collections.abc import Iterable, Mapping
from typing import Optional, Tuple
import re

from .declarative import Declarative
from .expression import Reference
from .registry import Registry


def class_to_label(name: str) -> str:
    """
    Convert Python class name (PascalCase with acronyms)
    to HCL-friendly snake_case.

    Examples:
        HttpServer    -> http_server
        XMLParser     -> xml_parser
        UserProfile   -> user_profile
    """
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


class Block(Declarative):
    """
    HCL block representation.

    Represents a generic HCL block as defined in the HCL language specification.
    A block consists of:
      - an optional sequence of labels (0..N)
      - a body containing attributes and/or nested blocks

    This class is format-agnostic and does NOT perform final rendering.
    It only builds a structured, nested representation that can later be
    rendered into HCL text, JSON-compatible forms, or any other backend.

    Examples (HCL):
      service "api" { ... }
      policy { ... }
      handler "json" { ... }

    Examples (PHCL):
      service = B["api"](...)
      policy = B(...)
      handler = B["json"](...)
    """

    _phcl_kind: Optional[str] = None
    _phcl_label: Optional[Tuple[str, ...]] = None

    @classmethod
    def __class_getitem__(cls, labels):
        if not isinstance(labels, tuple):
            labels = (labels,)

        return type(
            f"{cls.__name__}__" + "_".join(labels),
            (cls,),
            {
                "_phcl_label": labels,
                "_phcl_abstract": True,
            },
        )

    def __init__(self, **kwargs):
        for k in kwargs:
            if k.startswith("_"):
                raise ValueError("Attributes starting with '_' are reserved")
        self.__dict__.update(kwargs)

    def _phcl_normalize_attr(self, name, value):
        return value

    def _phcl_build(self, key: Optional[str] = None) -> dict:
        def emit(k, v):
            if isinstance(v, Block):
                return v._phcl_build()
            if isinstance(v, list):
                return [
                    emit(k, x) if isinstance(x, Block) else emit(None, x) for x in v
                ]
            if isinstance(v, Mapping):
                return {kk: emit(kk, vv) for kk, vv in v.items()}
            if isinstance(v, Iterable) and not isinstance(v, (str, bytes)):
                return [
                    emit(k, x) if isinstance(x, Block) else emit(None, x) for x in v
                ]
            return v

        body = {
            k: emit(k, self._phcl_normalize_attr(k, v))
            for k, v in self._phcl_attributes.items()
        }
        node = {key: body} if key else body

        for lbl in self._phcl_label or []:
            node = {lbl: node}

        return node

    def _phcl_render(self, v):
        if isinstance(v, Block):
            return {
                k: self._phcl_render(x)
                for k, x in v._phcl_attributes.items()
            }

        if isinstance(v, list):
            return [self._phcl_render(x) for x in v]

        if isinstance(v, Mapping):
            return {k: self._phcl_render(x) for k, x in v.items()}

        if isinstance(v, Iterable) and not isinstance(v, (str, bytes)):
            return [self._phcl_render(x) for x in v]

        return v

    def _phcl_spec(self) -> dict:
        labels = ((class_to_label(self.__class__.__name__),) + self._phcl_label) if self._phcl_label else ()
        return {
            "kind": self._phcl_kind,
            "labels": labels,
            "attrs": {
                k: self._phcl_render(self._phcl_normalize_attr(k, v))
                for k, v in self._phcl_attributes.items()
            },
        }


class Node(Block):
    """
    Base class for top-level renderable declarations.

    `Node` extends `Block` with registry behavior so framework layers can
    declare concrete classes and later emit them as a document.
    """

    _phcl_registry = Registry._phcl_registry

    @classmethod
    def _phcl_reference_base(cls) -> str:
        raise TypeError(f"{cls.__name__} is not addressable in reference-space")

    @classmethod
    def _phcl_logical_name(cls) -> str:
        return class_to_label(cls.__name__)

    @classmethod
    @property
    def _(cls):
        return Reference(cls._phcl_reference_base())

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls is not Node and Node in cls.__bases__ and "_phcl_kind" not in cls.__dict__:
            cls._phcl_kind = class_to_label(cls.__name__)

        if cls.__dict__.get("_phcl_abstract", False):
            return

        if cls is Node:
            return

        Registry.add(cls)

    def _phcl_build(self) -> dict:
        return super()._phcl_build(self.__class__._phcl_logical_name())
