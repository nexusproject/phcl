from phcl.core.expression import Expression, hcl
from phcl.syntax import hcl_templatefile


def test_syntax_hcl_templatefile_builds_expression_with_structural_vars():
    value = hcl_templatefile(
        "${path.module}/templates/user_data.sh.tftpl",
        {
            "app_name": hcl("var.app_name"),
            "port": 8080,
            "enable_metrics": True,
        },
    )

    assert isinstance(value, Expression)
    assert value.source == (
        'templatefile("${path.module}/templates/user_data.sh.tftpl", '
        "{app_name = var.app_name, port = 8080, enable_metrics = true})"
    )


def test_syntax_hcl_templatefile_accepts_expression_path():
    value = hcl_templatefile(
        hcl('format("%s/user_data.sh.tftpl", path.module)'),
        {},
    )

    assert value.source == 'templatefile(format("%s/user_data.sh.tftpl", path.module), {})'
