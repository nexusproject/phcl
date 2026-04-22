from phcl.core.expression import Expression
from phcl.syntax import hcl


def test_syntax_hcl_wraps_and_strips_source():
    value = hcl("  aws_instance.web.id  ")

    assert isinstance(value, Expression)
    assert value.source == "aws_instance.web.id"
    assert str(value) == "aws_instance.web.id"
