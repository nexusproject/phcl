import pytest

from phcl.core.expression import Expression
from phcl.runtime import render_file


def test_render_file_returns_heredoc_expression_by_default(tmp_path):
    path = tmp_path / "example.txt"
    path.write_text("hello\nworld\n", encoding="utf-8")

    value = render_file(path)

    assert isinstance(value, Expression)
    assert value.source == "<<-HEREDOC_EOF\nhello\nworld\nHEREDOC_EOF"


def test_render_file_can_return_plain_text(tmp_path):
    path = tmp_path / "example.txt"
    path.write_text("hello\nworld\n", encoding="utf-8")

    value = render_file(path, heredoc=False)

    assert value == "hello\nworld\n"


def test_render_file_applies_template_context_before_heredoc_wrapping(tmp_path):
    path = tmp_path / "example.tmpl"
    path.write_text("hello $name from $place\n", encoding="utf-8")

    value = render_file(
        path,
        context={
            "name": "dmitry",
            "place": "phcl",
        },
    )

    assert isinstance(value, Expression)
    assert value.source == "<<-HEREDOC_EOF\nhello dmitry from phcl\nHEREDOC_EOF"


def test_render_file_can_return_heredoc_expression(tmp_path):
    path = tmp_path / "script.sh"
    path.write_text("echo $word\n", encoding="utf-8")

    value = render_file(
        path,
        context={"word": "hello"},
        heredoc=True,
    )

    assert isinstance(value, Expression)
    assert value.source == "<<-HEREDOC_EOF\necho hello\nHEREDOC_EOF"


def test_render_file_multiline_remains_supported_alias(tmp_path):
    path = tmp_path / "script.sh"
    path.write_text("echo $word\n", encoding="utf-8")

    with pytest.warns(DeprecationWarning, match="heredoc"):
        value = render_file(
            path,
            context={"word": "hello"},
            multiline=True,
        )

    assert isinstance(value, Expression)
    assert value.source == "<<-MULTILINE_EOF\necho hello\nMULTILINE_EOF"


def test_render_file_multiline_false_remains_supported_alias_for_plain_text(tmp_path):
    path = tmp_path / "script.sh"
    path.write_text("echo hello\n", encoding="utf-8")

    with pytest.warns(DeprecationWarning, match="heredoc"):
        value = render_file(path, multiline=False)

    assert value == "echo hello\n"


def test_render_file_rejects_using_heredoc_and_multiline_together(tmp_path):
    path = tmp_path / "script.sh"
    path.write_text("echo hello\n", encoding="utf-8")

    with pytest.raises(ValueError, match="both heredoc and multiline"):
        render_file(path, heredoc=True, multiline=True)
