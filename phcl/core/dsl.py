from typing import Any, Dict, List, Type, Optional, Tuple
from pprint import pprint as p
import re
from dataclasses import dataclass


class Declarative:
    """
    Declarative DSL base.

    Provides declarative composition via inheritance:
    attributes defined on base classes are merged and overridden
    by subclasses to form the final configuration body.

    This class does not represent an HCL block itself —
    it only defines *what* should be rendered, not *how*.
    """

    @property
    def _phcl_attributes(self) -> Dict[str, Any]:
        attrs: Dict[str, Any] = {}

        for base in list(reversed(self.__class__.mro())) + [self]:
            if base is Declarative:
                continue

            for name, value in base.__dict__.items():
                if name.startswith("_"):
                    continue

                # skip methods, keep classes and properties
                if callable(value) and not isinstance(value, (property, type)):
                    continue

                if isinstance(value, property):
                    attrs[name] = getattr(self, name)
                else:
                    attrs[name] = value

        return attrs


def class_to_label(name: str) -> str:
    """
    Convert Python class name (PascalCase with acronyms)
    to Terraform-style snake_case.

    Examples:
        WebEC2        -> web_ec2
        IAMRole      -> iam_role
        ALBListener  -> alb_listener
    """
    # split before last capital in acronym sequences
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
    rendered into Terraform JSON, HCL text, or any other backend.

    Examples (HCL):
      backend "s3" { ... }
      ingress { ... }
      provisioner "file" { ... }

    Examples (PHCL):
      backend = B["s3"](...)
      ingress = B(...)
      provisioner = B["file"](...)
    """
    _phcl_kind: str | None = None
    _phcl_label: tuple[str, ...] | None = None

    @classmethod
    def __class_getitem__(cls, labels):
        if not isinstance(labels, tuple):
            labels = (labels,)

        print("--> ", labels)

        return type(
            f"{cls.__name__}__" + "_".join(labels),
            (cls,),
            {"_phcl_label": labels},
        )

    def __init__(self, **kwargs):
        for k in kwargs:
            if k.startswith("_"):
                raise ValueError("Attributes starting with '_' are reserved")
        self.__dict__.update(kwargs)

    def _phcl_build(self, key: Optional[str] = None) -> dict:
        def emit(k, v):
            if isinstance(v, Block):
                return v._phcl_build()
            if isinstance(v, list):
                return [
                    emit(k, x) if isinstance(x, Block) else emit(None, x) for x in v
                ]
            if isinstance(v, dict):
                return {kk: emit(kk, vv) for kk, vv in v.items()}
            return v

        body = {k: emit(k, v) for k, v in self._phcl_attributes.items()}
        node = {key: body} if key else body

        # Apply block labels as outer nesting levels (HCL JSON semantics)
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

        if isinstance(v, dict):
            return {k: self._phcl_render(x) for k, x in v.items()}

        return v

    def _phcl_spec(self) -> dict:
        return {
            "kind": self._phcl_kind,
            "labels": (class_to_label(self.__class__.__name__),) + self._phcl_label or (),
            "attrs": {k: self._phcl_render(v) for k, v in self._phcl_attributes.items()},
        }


