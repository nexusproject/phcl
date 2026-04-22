from phcl.core.expression import Expression, hcl
from phcl.syntax import file


def test_syntax_file_wraps_string_path_as_hcl_function_call():
    value = file("${path.module}/script.sh")

    assert isinstance(value, Expression)
    assert value.source == 'file("${path.module}/script.sh")'


def test_syntax_file_accepts_expression_path():
    value = file(hcl('format("%s/bootstrap.sh", path.module)'))

    assert value.source == 'file(format("%s/bootstrap.sh", path.module))'
