from phcl.core.expression import Expression
from phcl.runtime import multiline


def test_multiline_wraps_python_string_as_heredoc_expression():
    value = multiline("line one\nline two")

    assert isinstance(value, Expression)
    assert value.source == "<<-MULTILINE_EOF\nline one\nline two\nMULTILINE_EOF"


def test_multiline_trims_single_trailing_newline_before_wrapping():
    value = multiline("line one\nline two\n")

    assert value.source == "<<-MULTILINE_EOF\nline one\nline two\nMULTILINE_EOF"


def test_multiline_allows_custom_marker():
    value = multiline("echo hello", marker="SCRIPT")

    assert value.source == "<<-SCRIPT\necho hello\nSCRIPT"
