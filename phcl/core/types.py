from __future__ import annotations

from collections.abc import Mapping, Sequence

from .expression import Expression


class TypeExpression(Expression):
    """Opaque HCL type expression fragment."""


def _coerce_type(value) -> TypeExpression:
    if isinstance(value, TypeExpression):
        return value

    raise TypeError(f"Unsupported HCL type expression: {value!r}")


def _render_type(value) -> str:
    return _coerce_type(value).source


def _call(name: str, *args) -> TypeExpression:
    rendered = ", ".join(_render_type(arg) for arg in args)
    return TypeExpression(f"{name}({rendered})")


def LIST(inner) -> TypeExpression:
    return _call("list", inner)


def MAP(inner) -> TypeExpression:
    return _call("map", inner)


def SET(inner) -> TypeExpression:
    return _call("set", inner)


def OPTIONAL(inner) -> TypeExpression:
    return _call("optional", inner)


def TUPLE(items: Sequence) -> TypeExpression:
    rendered = ", ".join(_render_type(item) for item in items)
    return TypeExpression(f"tuple([{rendered}])")


def OBJECT(attrs: Mapping[str, object]) -> TypeExpression:
    if not isinstance(attrs, Mapping):
        raise TypeError("OBJECT(...) expects a mapping of attribute names to type expressions")

    rendered = ", ".join(f"{key} = {_render_type(value)}" for key, value in attrs.items())
    return TypeExpression(f"object({{{rendered}}})")


STRING = TypeExpression("string")
NUMBER = TypeExpression("number")
BOOL = TypeExpression("bool")
ANY = TypeExpression("any")

