from phcl.core.expression import Expression, hcl
from phcl.syntax import hcl_format


def test_syntax_hcl_format_builds_expression_from_structural_arguments():
    value = hcl_format("%s/*", hcl("aws_s3_bucket.frontend.arn"))

    assert isinstance(value, Expression)
    assert value.source == 'format("%s/*", aws_s3_bucket.frontend.arn)'


def test_syntax_hcl_format_accepts_expression_format_string():
    value = hcl_format(hcl("var.pattern"), "api")

    assert value.source == 'format(var.pattern, "api")'
