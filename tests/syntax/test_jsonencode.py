import pytest

from phcl.core.expression import Expression
from phcl.syntax import hcl, hcl_jsonencode, jsonencode


def test_syntax_hcl_jsonencode_builds_expression_from_structural_python_values():
    value = hcl_jsonencode(
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


def test_syntax_jsonencode_remains_supported_alias():
    with pytest.warns(DeprecationWarning, match="hcl_jsonencode"):
        value = jsonencode({"name": "api"})

    assert value.source == hcl_jsonencode({"name": "api"}).source
