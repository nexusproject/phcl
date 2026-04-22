from phcl.core.expression import Expression
from phcl.runtime import render_file


def test_render_file_reads_plain_text(tmp_path):
    path = tmp_path / "example.txt"
    path.write_text("hello\nworld\n", encoding="utf-8")

    value = render_file(path)

    assert value == "hello\nworld\n"


def test_render_file_applies_template_context(tmp_path):
    path = tmp_path / "example.tmpl"
    path.write_text("hello $name from $place\n", encoding="utf-8")

    value = render_file(
        path,
        context={
            "name": "dmitry",
            "place": "phcl",
        },
    )

    assert value == "hello dmitry from phcl\n"


def test_render_file_can_return_multiline_expression(tmp_path):
    path = tmp_path / "script.sh"
    path.write_text("echo $word\n", encoding="utf-8")

    value = render_file(
        path,
        context={"word": "hello"},
        multiline=True,
    )

    assert isinstance(value, Expression)
    assert value.source == "<<-MULTILINE_EOF\necho hello\nMULTILINE_EOF"
