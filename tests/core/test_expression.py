import pytest

from phcl.core.expression import Expression, Reference, hcl, jsonencode


def test_hcl_wraps_and_strips_source():
    value = hcl("  aws_instance.web.id  ")

    assert isinstance(value, Expression)
    assert value.source == "aws_instance.web.id"
    assert str(value) == "aws_instance.web.id"


def test_expression_repr_is_stable():
    value = Expression("var.region")

    assert repr(value) == "Expression('var.region')"


def test_expression_cannot_be_used_in_boolean_context():
    value = hcl("var.enabled")

    with pytest.raises(TypeError, match="boolean context"):
        bool(value)


def test_reference_supports_attribute_traversal():
    ref = Reference("aws_instance.web").id

    assert isinstance(ref, Reference)
    assert isinstance(ref, Expression)
    assert str(ref) == "aws_instance.web.id"


def test_reference_rejects_private_attribute_traversal():
    ref = Reference("aws_instance.web")

    with pytest.raises(AttributeError):
        _ = ref._secret


def test_reference_supports_indexing_with_string_expression_and_reference():
    base = Reference("module.network")

    assert str(base["public"]) == 'module.network["public"]'
    assert str(base[hcl("var.key")]) == "module.network[var.key]"
    assert str(base[Reference("each.key")]) == "module.network[each.key]"


def test_reference_repr_is_stable():
    ref = Reference("var.region")

    assert repr(ref) == "Reference('var.region')"


def test_jsonencode_builds_expression_from_structural_python_values():
    value = jsonencode(
        [
            {
                "name": "api",
                "image": hcl("var.app_image"),
                "ports": (port for port in (8080, 8443)),
                "enabled": True,
            }
        ]
    )

    assert isinstance(value, Expression)
    assert value.source == (
        'jsonencode([{name = "api", image = var.app_image, ports = [8080, 8443], enabled = true}])'
    )
