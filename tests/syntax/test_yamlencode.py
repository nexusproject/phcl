from phcl.core.expression import Expression
from phcl.syntax import hcl, hcl_yamlencode


def test_syntax_hcl_yamlencode_builds_expression_from_structural_python_values():
    value = hcl_yamlencode(
        {
            "name": "api",
            "ports": [8080, 8443],
            "enabled": hcl("var.enabled"),
        }
    )

    assert isinstance(value, Expression)
    assert value.source == (
        "yamlencode({name = \"api\", ports = [8080, 8443], enabled = var.enabled})"
    )
