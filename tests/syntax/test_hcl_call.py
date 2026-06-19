from phcl.core.expression import Expression
import phcl.syntax as syntax
from phcl.syntax import hcl, hcl_call


def test_syntax_hcl_call_builds_expression_from_structural_python_values():
    value = hcl_call(
        "merge",
        {"name": "api"},
        {"image": hcl("var.app_image")},
    )

    assert isinstance(value, Expression)
    assert value.source == 'merge({name = "api"}, {image = var.app_image})'


def test_syntax_hcl_call_allows_function_name_to_be_chosen_at_runtime():
    function_name = "coalesce"

    value = hcl_call(function_name, hcl("var.name"), "default")

    assert value.source == 'coalesce(var.name, "default")'


def test_syntax_hcl_call_rejects_empty_function_name():
    try:
        hcl_call("  ")
    except ValueError as exc:
        assert str(exc) == "HCL function name cannot be empty"
    else:
        raise AssertionError("hcl_call should reject an empty function name")


def test_syntax_all_exposes_new_hcl_function_surface_only():
    assert "hcl_call" in syntax.__all__
    assert "hcl_file" in syntax.__all__
    assert "hcl_format" in syntax.__all__
    assert "hcl_jsonencode" in syntax.__all__
    assert "label" in syntax.__all__
    assert "file" not in syntax.__all__
    assert "jsonencode" not in syntax.__all__
