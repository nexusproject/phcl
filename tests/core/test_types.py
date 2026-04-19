import pytest

from phcl.core.types import ANY, BOOL, LIST, MAP, NUMBER, OBJECT, OPTIONAL, SET, STRING, TUPLE, TypeExpression
from phcl.render.hcl2 import render_value


def test_primitive_type_expressions_render_as_raw_hcl_tokens():
    assert isinstance(STRING, TypeExpression)
    assert render_value(STRING) == "string"
    assert render_value(NUMBER) == "number"
    assert render_value(BOOL) == "bool"
    assert render_value(ANY) == "any"


def test_composed_type_expressions_render_as_hcl_type_syntax():
    assert render_value(LIST(STRING)) == "list(string)"
    assert render_value(MAP(STRING)) == "map(string)"
    assert render_value(SET(NUMBER)) == "set(number)"
    assert render_value(OPTIONAL(BOOL)) == "optional(bool)"
    assert render_value(TUPLE([STRING, NUMBER])) == "tuple([string, number])"
    assert render_value(OBJECT({"name": STRING, "enabled": OPTIONAL(BOOL)})) == (
        "object({name = string, enabled = optional(bool)})"
    )


def test_object_type_requires_mapping():
    with pytest.raises(TypeError, match="expects a mapping"):
        OBJECT([STRING])


def test_type_constructors_reject_non_type_arguments():
    with pytest.raises(TypeError, match="Unsupported HCL type expression"):
        LIST("string")
