from argparse import Namespace
from pathlib import Path

import pytest

from phcl.cli.phcl import (
    build_parser,
    command_build,
    compile_file,
    discover_python_files,
    load_file_config,
    normalize_extension,
    output_path_for,
)
from phcl.core import Declarative
from phcl.core.registry import Registry


def write_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_normalize_extension_adds_leading_dot():
    assert normalize_extension("tf") == ".tf"
    assert normalize_extension(".tf") == ".tf"


def test_build_parser_supports_short_version_flag(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["-V"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("phcl ")


def test_load_file_config_returns_none_when_phcl_is_missing():
    assert load_file_config({}) is None


def test_load_file_config_reads_extension_skip_and_indentation():
    class PHCL:
        extension = "tf"
        skip = True
        indentation = " " * 4

    config = load_file_config({"PHCL": PHCL})

    assert config is not None
    assert config.extension == ".tf"
    assert config.skip is True
    assert config.indentation == " " * 4


def test_load_file_config_reads_declarative_phcl_class():
    class BaseSettings(Declarative):
        extension = "tf"
        indentation = " " * 2

    class PHCL(BaseSettings):
        indentation = " " * 4
        skip = True

    config = load_file_config({"PHCL": PHCL})

    assert config is not None
    assert config.extension == ".tf"
    assert config.skip is True
    assert config.indentation == " " * 4


def test_discover_python_files_skips_pycache(tmp_path):
    write_file(tmp_path / "a.py", "x = 1\n")
    write_file(tmp_path / "nested" / "b.py", "x = 2\n")
    write_file(tmp_path / "__pycache__" / "skip.py", "x = 3\n")

    files = discover_python_files(tmp_path)

    assert files == [
        tmp_path / "a.py",
        tmp_path / "nested" / "b.py",
    ]


def test_output_path_for_in_place_generation_uses_only_python_suffix(tmp_path):
    source = tmp_path / "examples" / "aws.tf.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.touch()

    output = output_path_for(source, tmp_path, None, ".tf")

    assert output == tmp_path / "examples" / "aws.tf"


def test_output_path_for_out_dir_mirrors_tree(tmp_path):
    source = tmp_path / "examples" / "packer.config.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.touch()

    output = output_path_for(source, tmp_path, tmp_path / "dist", ".pkr.hcl")

    assert output == tmp_path / "dist" / "examples" / "packer.config.pkr.hcl"


def test_compile_file_skips_when_phcl_config_is_missing(tmp_path):
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

    assert result.status == "ignore"
    assert result.detail == ""


def test_compile_file_skips_when_phcl_requests_skip(tmp_path):
    source = write_file(
        tmp_path / "service.py",
        """
class PHCL:
    extension = "tf"
    skip = True
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

    assert result.status == "skip"
    assert result.detail == "disabled"


def test_compile_file_exposes_path_target_during_module_loading(tmp_path):
    source = write_file(
        tmp_path / "src" / "check_target.py",
        f"""
from pathlib import Path
from phcl.runtime import path_target

if path_target() != Path({str(tmp_path / "src")!r}):
    raise RuntimeError(f"unexpected target: {{path_target()}}")

class PHCL:
    skip = True
""".strip()
        + "\n",
    )

    result = compile_file(
        source,
        base=tmp_path / "src",
        out_dir=None,
        ext=".tf",
        stdout=False,
    )

    assert result.status == "skip"


def test_compile_file_formats_file_backed_errors_relative_to_build_target(tmp_path):
    source = write_file(
        tmp_path / "src" / "invalid.py",
        """
from phcl.runtime import path_module, yaml_block

Invalid = yaml_block(path_module() / "invalid.yaml", at="dev")
""".strip()
        + "\n",
    )
    write_file(
        tmp_path / "src" / "invalid.yaml",
        """
dev:
  AWS:SourceArn: api
""".strip()
        + "\n",
    )

    result = compile_file(
        source,
        base=tmp_path / "src",
        out_dir=None,
        ext=".tf",
        stdout=False,
    )

    assert result.status == "fail"
    assert "invalid.yaml selection at='dev'" in result.detail
    assert str(tmp_path) not in result.detail


def test_compile_file_writes_rendered_output_from_phcl_config(tmp_path):
    source = write_file(
        tmp_path / "service.py",
        """
class PHCL:
    extension = "tf"

from phcl.core.nodes import Node

class Service(Node):
    _phcl_kind = "service"

class Web(Service):
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

    assert result.status == "write", result.detail
    assert result.output == tmp_path / "out" / "service.tf"
    assert result.output.read_text(encoding="utf-8") == (
        'service "web" {\n'
        '  instance_type = "t3.micro"\n'
        '}\n'
    )
    assert Registry.renderables() == []


def test_compile_file_collects_deprecation_warnings(tmp_path):
    source = write_file(
        tmp_path / "service.py",
        """
class PHCL:
    extension = "tf"

from phcl.core.nodes import Node
from phcl.syntax import jsonencode

class Service(Node):
    _phcl_kind = "service"

class Web(Service):
    config = jsonencode({"name": "api"})
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

    assert result.status == "write"
    assert result.warnings is not None
    assert len(result.warnings) == 1
    assert "jsonencode" in result.warnings[0].message
    assert result.warnings[0].filename == str(source)


def test_compile_file_supports_imported_global_phcl_config_and_local_render_options(tmp_path):
    package_dir = tmp_path / "infra"
    write_file(
        package_dir / "config.py",
        """
class GlobalSettings:
    extension = "tf"
    indentation = " " * 4
""".strip()
        + "\n",
    )
    source = write_file(
        package_dir / "service.py",
        """
from .config import GlobalSettings as PHCL
from phcl.core.nodes import Node

class Service(Node):
    _phcl_kind = "service"

class Web(Service):
    instance_type = "t3.micro"
""".strip()
        + "\n",
    )

    result = compile_file(
        source,
        base=package_dir,
        out_dir=None,
        ext=None,
        stdout=False,
    )

    assert result.status == "write", result.detail
    assert result.output == package_dir / "service.tf"
    assert result.output.read_text(encoding="utf-8") == (
        'service "web" {\n'
        '    instance_type = "t3.micro"\n'
        '}\n'
    )


def test_compile_file_supports_local_phcl_inheritance_override(tmp_path):
    package_dir = tmp_path / "infra"
    write_file(
        package_dir / "config.py",
        """
class GlobalSettings:
    extension = "tf"
    indentation = " " * 2
""".strip()
        + "\n",
    )
    source = write_file(
        package_dir / "service.py",
        """
from .config import GlobalSettings
from phcl.core.nodes import Node

class PHCL(GlobalSettings):
    indentation = " " * 4

class Service(Node):
    _phcl_kind = "service"

class Web(Service):
    instance_type = "t3.micro"
""".strip()
        + "\n",
    )

    result = compile_file(
        source,
        base=package_dir,
        out_dir=None,
        ext=None,
        stdout=False,
    )

    assert result.status == "write", result.detail
    assert result.output.read_text(encoding="utf-8") == (
        'service "web" {\n'
        '    instance_type = "t3.micro"\n'
        '}\n'
    )


def test_compile_file_does_not_render_imported_declarations_from_phcl_config_module(tmp_path):
    package_dir = tmp_path / "infra"
    write_file(
        package_dir / "config.py",
        """
class PHCL:
    extension = "tf"

from phcl.core.nodes import Node

class Thing(Node):
    _phcl_kind = "thing"

class Imported(Thing):
    source = "config"
""".strip()
        + "\n",
    )
    source = write_file(
        package_dir / "registry.py",
        """
from .config import PHCL
from phcl.core.nodes import Node

class Thing(Node):
    _phcl_kind = "thing"

class Local(Thing):
    source = "registry"
""".strip()
        + "\n",
    )

    result = compile_file(
        source,
        base=package_dir,
        out_dir=None,
        ext=None,
        stdout=False,
    )

    assert result.status == "write", result.detail
    assert result.output.read_text(encoding="utf-8") == (
        'thing "local" {\n'
        '  source = "registry"\n'
        '}\n'
    )

def test_compile_file_falls_back_to_cli_extension_override(tmp_path):
    source = write_file(
        tmp_path / "service.py",
        """
class PHCL:
    indentation = " " * 2

from phcl.core.nodes import Node

class Service(Node):
    _phcl_kind = "service"

class Web(Service):
    instance_type = "t3.micro"
""".strip()
        + "\n",
    )

    result = compile_file(
        source,
        base=tmp_path,
        out_dir=None,
        ext=".tf",
        stdout=False,
    )

    assert result.status == "write"
    assert result.output == tmp_path / "service.tf"


def test_compile_file_defaults_to_hcl_when_phcl_extension_is_missing(tmp_path):
    source = write_file(
        tmp_path / "service.py",
        """
class PHCL:
    pass

from phcl.core.nodes import Node

class Service(Node):
    _phcl_kind = "service"

class Web(Service):
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

    assert result.status == "write"
    assert result.output == tmp_path / "service.hcl"
    assert result.output.read_text(encoding="utf-8") == (
        'service "web" {\n'
        '  instance_type = "t3.micro"\n'
        '}\n'
    )


def test_compile_file_returns_fail_on_execution_error(tmp_path):
    source = write_file(
        tmp_path / "broken.py",
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


def test_compile_file_returns_fail_on_render_error(tmp_path):
    source = write_file(
        tmp_path / "broken_render.py",
        """
class PHCL:
    extension = "tf"

from phcl.runtime import this
from phcl.core.nodes import Node

class Resource(Node["example"]):
    _phcl_kind = "resource"

class Broken(Resource):
    name = this.key
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
    assert result.output is None
    assert result.detail == "`this` is only available inside `generate(...)`"
    assert Registry.renderables() == []


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
        tmp_path / "broken.py",
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


def test_command_build_prints_deprecation_warnings(tmp_path, capsys):
    source = write_file(
        tmp_path / "service.py",
        """
class PHCL:
    extension = "tf"

from phcl.core.nodes import Node
from phcl.syntax import jsonencode

class Service(Node):
    _phcl_kind = "service"

class Web(Service):
    config = jsonencode({"name": "api"})
""".strip()
        + "\n",
    )

    args = Namespace(
        target=str(source),
        out_dir=None,
        ext=None,
        stdout=False,
        quiet=False,
    )

    code = command_build(args)
    captured = capsys.readouterr()

    assert code == 0
    assert "warn" in captured.err
    assert "jsonencode" in captured.err
    assert "service.py:" in captured.err
    assert "1 warnings" in captured.out


def test_command_build_deduplicates_imported_deprecation_warnings(tmp_path, capsys):
    package_dir = tmp_path / "infra"
    write_file(package_dir / "__init__.py", "")
    write_file(
        package_dir / "shared.py",
        """
from phcl.syntax import jsonencode

SHARED = jsonencode({"name": "api"})
""".strip()
        + "\n",
    )
    write_file(
        package_dir / "one.py",
        """
class PHCL:
    extension = "tf"

from .shared import SHARED
from phcl.core.nodes import Node

class Thing(Node):
    _phcl_kind = "thing"

class One(Thing):
    config = SHARED
""".strip()
        + "\n",
    )
    write_file(
        package_dir / "two.py",
        """
class PHCL:
    extension = "tf"

from .shared import SHARED
from phcl.core.nodes import Node

class Thing(Node):
    _phcl_kind = "thing"

class Two(Thing):
    config = SHARED
""".strip()
        + "\n",
    )

    args = Namespace(
        target=str(package_dir),
        out_dir=None,
        ext=None,
        stdout=False,
        quiet=False,
    )

    code = command_build(args)
    captured = capsys.readouterr()

    assert code == 0
    assert captured.err.count("warn") == 1
    assert "jsonencode" in captured.err
    assert "shared.py:" in captured.err
    assert "1 warnings" in captured.out
