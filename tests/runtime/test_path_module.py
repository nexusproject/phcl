import importlib.util
import sys
from pathlib import Path

import pytest

from phcl.runtime import path_target


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_path_module_returns_calling_module_directory(tmp_path):
    module_path = tmp_path / "infra" / "config.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text(
        """
from phcl.runtime import path_module

MODULE_DIR = path_module()
""".strip()
        + "\n",
        encoding="utf-8",
    )

    module = load_module(module_path, "test_runtime_module")

    assert module.MODULE_DIR == module_path.parent.resolve()


def test_path_target_requires_phcl_build_context():
    with pytest.raises(RuntimeError, match="phcl build"):
        path_target()
