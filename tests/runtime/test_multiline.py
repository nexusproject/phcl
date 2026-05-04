import pytest

from phcl.core.expression import Expression
from phcl.runtime import heredoc, multiline


def test_heredoc_wraps_python_string_as_heredoc_expression():
    value = heredoc("line one\nline two")

    assert isinstance(value, Expression)
    assert value.source == "<<-HEREDOC_EOF\nline one\nline two\nHEREDOC_EOF"


def test_heredoc_trims_single_trailing_newline_before_wrapping():
    value = heredoc("line one\nline two\n")

    assert value.source == "<<-HEREDOC_EOF\nline one\nline two\nHEREDOC_EOF"


def test_heredoc_allows_custom_marker():
    value = heredoc("echo hello", marker="SCRIPT")

    assert value.source == "<<-SCRIPT\necho hello\nSCRIPT"


def test_multiline_remains_supported_alias():
    with pytest.warns(DeprecationWarning, match="heredoc"):
        value = multiline("line one\nline two")

    assert value.source == "<<-MULTILINE_EOF\nline one\nline two\nMULTILINE_EOF"
