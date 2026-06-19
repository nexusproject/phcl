from collections.abc import Mapping
from typing import Optional, Tuple
import re

from .declarative import Declarative
from .expression import Reference
from .registry import Registry
from .values import normalize_value


class _GenerationContext:
    def __init__(self, *, generated_cls, index, key, value):
        self.generated_cls = generated_cls
        self.index = index
        self.key = key
        self.value = value

    @property
    def label(self):
        if not getattr(self.generated_cls, "_phcl_auto_label", True):
            return None
        return self.generated_cls._phcl_logical_name()


class _ClassProperty:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner=None):
        if owner is None:
            owner = type(instance)
        return self.fget(owner)


class _GeneratedTemplateReference:
    def __init__(self, cls):
        self.cls = cls

    def __getitem__(self, key: str):
        classes = self.cls.__dict__.get("_phcl_generation_classes", {})
        try:
            generated_cls = classes[key]
        except KeyError as exc:
            raise KeyError(
                f"{self.cls.__name__} has no generated declaration for key {key!r}"
            ) from exc
        return Reference(generated_cls._phcl_reference_base())

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        raise TypeError(
            f"{self.cls.__name__} is a generated template; select a generated "
            f"declaration with {self.cls.__name__}._[\"key\"]"
        )


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
    _phcl_auto_label = True

    @classmethod
    def __class_getitem__(cls, labels):
        if not isinstance(labels, tuple):
            labels = (labels,)

        return type(
            f"{cls.__name__}__" + "__".join(labels),
            (cls,),
            {
                "_phcl_label": labels,
                "_phcl_abstract": True,
            },
        )

    def __init__(self, /, **kwargs):
        for k in kwargs:
            if k == "_":
                raise ValueError("Attribute '_' is reserved")
            if k.startswith("_phcl_"):
                raise ValueError("Attributes starting with '_phcl_' are reserved")
        self.__dict__.update(kwargs)

    @property
    def _phcl_attributes(self):
        attrs = super()._phcl_attributes
        item = self.__class__._phcl_generation_item()
        if item is None:
            return attrs
        return {
            name: self._phcl_resolve_generation_value(value, item)
            for name, value in attrs.items()
        }

    @classmethod
    def _phcl_generation_item(cls):
        key = cls.__dict__.get("_phcl_generation_key")
        if key is None:
            return None

        for base in cls.__mro__[1:]:
            if "_phcl_generation_source" not in base.__dict__:
                continue

            source = base.__dict__["_phcl_generation_source"]
            if isinstance(source, Mapping):
                for index, item_key in enumerate(source):
                    if item_key == key:
                        return _GenerationContext(
                            generated_cls=cls,
                            index=index,
                            key=key,
                            value=source[key],
                        )
            elif isinstance(source, list):
                index = int(key)
                return _GenerationContext(
                    generated_cls=cls,
                    index=index,
                    key=key,
                    value=source[index],
                )

        return None

    @classmethod
    def _phcl_resolve_generation_value(cls, value, item):
        resolve = getattr(value, "_phcl_resolve", None)
        if resolve is not None:
            return resolve(item)

        if isinstance(value, list):
            return [cls._phcl_resolve_generation_value(x, item) for x in value]

        if isinstance(value, tuple):
            return tuple(cls._phcl_resolve_generation_value(x, item) for x in value)

        if isinstance(value, Mapping):
            return {
                key: cls._phcl_resolve_generation_value(x, item)
                for key, x in value.items()
            }

        return value

    def _phcl_normalize_value(self, value):
        def coerce(item):
            if isinstance(item, type) and issubclass(item, Node):
                return item._
            if isinstance(item, type) and issubclass(item, Block):
                return item()
            return item

        return normalize_value(value, passthrough_types=(Block,), coerce=coerce)

    def _phcl_normalize_attr(self, name, value):
        """
        Hook for product-specific attribute normalization.

        The core normalizes generic Python values into PHCL's structural value
        model by default. Higher-level layers can override this to adapt
        special fields before rendering or spec generation.
        """
        return self._phcl_normalize_value(value)

    def _phcl_spec(self) -> dict:
        def emit(v):
            if isinstance(v, Block):
                return {
                    k: emit(x)
                    for k, x in v._phcl_attributes.items()
                }

            if isinstance(v, list):
                return [emit(x) for x in v]

            if isinstance(v, Mapping):
                return {k: emit(x) for k, x in v.items()}

            return v

        labels = ((class_to_label(self.__class__.__name__),) + self._phcl_label) if self._phcl_label else ()
        return {
            "kind": self._phcl_kind,
            "labels": labels,
            "attrs": {
                k: emit(self._phcl_normalize_attr(k, v))
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
        """
        Return the declaration identity used as the final HCL block label.

        Structural labels such as Resource["aws_s3_bucket"] live in
        `_phcl_label`; this method only computes the trailing logical label.
        """
        override = cls.__dict__.get("_phcl_label_override")
        if override is not None:
            return override

        key = cls.__dict__.get("_phcl_generation_key")
        if key is not None:
            for base in cls.__mro__[1:]:
                if "_phcl_generation_source" in base.__dict__:
                    return f"{base._phcl_logical_name()}_{key}"

        return class_to_label(cls.__name__)

    @_ClassProperty
    def _(cls):
        if cls.__dict__.get("_phcl_generated_template", False):
            return _GeneratedTemplateReference(cls)
        return Reference(cls._phcl_reference_base())

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        generated_bases = [
            base
            for base in cls.__bases__
            if getattr(base, "_phcl_generated_template", False)
        ]
        if generated_bases and not cls.__dict__.get("_phcl_generated_materialization", False):
            base = generated_bases[0]
            raise TypeError(
                f"cannot subclass generated template {base.__name__}; "
                "inherit from a base declaration before applying generate(...)"
            )

        if cls is not Node and Node in cls.__bases__ and "_phcl_kind" not in cls.__dict__:
            cls._phcl_kind = class_to_label(cls.__name__)

        if cls is Node:
            return

        # Direct children of Node are language/product roots, not project
        # declarations. Concrete project declarations start one level deeper.
        if Node in cls.__bases__:
            return

        Registry.add(cls)
