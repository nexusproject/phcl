from phcl.core.expression import Expression
from phcl.syntax import hcl, jsonencode


def test_syntax_jsonencode_builds_expression_from_structural_python_values():
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
