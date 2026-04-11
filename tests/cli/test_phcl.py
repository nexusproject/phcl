from argparse import Namespace
from pathlib import Path

from phcl.cli.phcl import (
    command_build,
    compile_file,
    discover_python_files,
    infer_output_extension,
    output_path_for,
)
from phcl.core.registry import Registry


def write_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_infer_output_extension_from_python_source_name():
    assert infer_output_extension(Path("main.tf.py")) == ".tf"
    assert infer_output_extension(Path("image.pkr.hcl.py")) == ".pkr.hcl"
    assert infer_output_extension(Path("plain.py")) is None
    assert infer_output_extension(Path("plain.tf")) is None


def test_discover_python_files_skips_pycache(tmp_path):
    write_file(tmp_path / "a.py", "x = 1\n")
    write_file(tmp_path / "nested" / "b.py", "x = 2\n")
    write_file(tmp_path / "__pycache__" / "skip.py", "x = 3\n")

    files = discover_python_files(tmp_path)

    assert files == [
        tmp_path / "a.py",
        tmp_path / "nested" / "b.py",
    ]


def test_output_path_for_in_place_generation(tmp_path):
    source = tmp_path / "examples" / "aws.tf.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.touch()

    output = output_path_for(source, tmp_path, None, ".tf")

    assert output == tmp_path / "examples" / "aws.tf"


def test_output_path_for_out_dir_mirrors_tree(tmp_path):
    source = tmp_path / "examples" / "packer" / "image.pkr.hcl.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.touch()

    output = output_path_for(source, tmp_path, tmp_path / "dist", ".pkr.hcl")

    assert output == tmp_path / "dist" / "examples" / "packer" / "image.pkr.hcl"


def test_compile_file_writes_rendered_output(tmp_path):
    source = write_file(
        tmp_path / "service.tf.py",
        """
from phcl.core.nodes import Node

class Web(Node):
    _phcl_kind = "service"
    instance_type = "t3.micro"
""".strip()
        + "\n",
    )

    result = compile_file(
        source,
        base=tmp_path,
        out_dir=tmp_path / "out",
        ext=None,
        stdout=False,
    )

    assert result.status == "write"
    assert result.output == tmp_path / "out" / "service.tf"
    assert result.output.read_text(encoding="utf-8") == (
        'service "web" {\n'
        '  instance_type = "t3.micro"\n'
        '}\n'
    )
    assert Registry.renderables() == []


def test_compile_file_skips_when_registry_is_empty(tmp_path):
    source = write_file(
        tmp_path / "helper.py",
        "value = 42\n",
    )

    result = compile_file(
        source,
        base=tmp_path,
        out_dir=None,
        ext=".tf",
        stdout=False,
    )

    assert result.status == "skip"
    assert result.detail == "registry is empty"


def test_compile_file_fails_when_extension_cannot_be_inferred(tmp_path):
    source = write_file(
        tmp_path / "service.py",
        """
from phcl.core.nodes import Node

class Web(Node):
    _phcl_kind = "service"
    instance_type = "t3.micro"
""".strip()
        + "\n",
    )

    result = compile_file(
        source,
        base=tmp_path,
        out_dir=None,
        ext=None,
        stdout=False,
    )

    assert result.status == "fail"
    assert "cannot infer output extension" in result.detail


def test_compile_file_returns_fail_on_execution_error(tmp_path):
    source = write_file(
        tmp_path / "broken.tf.py",
        "raise RuntimeError('boom')\n",
    )

    result = compile_file(
        source,
        base=tmp_path,
        out_dir=None,
        ext=".tf",
        stdout=False,
    )

    assert result.status == "fail"
    assert "boom" in result.detail


def test_command_build_rejects_stdout_for_directory(tmp_path, capsys):
    args = Namespace(
        target=str(tmp_path),
        out_dir=None,
        ext=".tf",
        stdout=True,
    )

    code = command_build(args)
    captured = capsys.readouterr()

    assert code == 1
    assert "--stdout can only be used with a single file target" in captured.err


def test_command_build_reports_failures_in_stdout_mode(tmp_path, capsys):
    source = write_file(
        tmp_path / "broken.tf.py",
        "raise RuntimeError('boom')\n",
    )

    args = Namespace(
        target=str(source),
        out_dir=None,
        ext=".tf",
        stdout=True,
    )

    code = command_build(args)
    captured = capsys.readouterr()

    assert code == 1
    assert "fail" in captured.err
    assert "boom" in captured.err
