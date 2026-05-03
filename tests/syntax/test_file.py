import pytest

from phcl.core.expression import Expression, hcl
from phcl.syntax import file, hcl_file


def test_syntax_hcl_file_wraps_string_path_as_hcl_function_call():
    value = hcl_file("${path.module}/script.sh")

    assert isinstance(value, Expression)
    assert value.source == 'file("${path.module}/script.sh")'


def test_syntax_hcl_file_accepts_expression_path():
    value = hcl_file(hcl('format("%s/bootstrap.sh", path.module)'))

    assert value.source == 'file(format("%s/bootstrap.sh", path.module))'


def test_syntax_file_remains_supported_alias():
    with pytest.warns(DeprecationWarning, match="hcl_file"):
        value = file("policy.json")

    assert value.source == hcl_file("policy.json").source
