import importlib
import io
import runpy
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Optional


def is_valid_module_part(value: str) -> bool:
    return value.isidentifier()


def resolve_module_target(source: Path, base: Path) -> Optional[tuple[Path, str]]:
    source = source.resolve()
    base = base.resolve()
    candidates = []
    cwd = Path.cwd().resolve()

    if base.is_dir():
        if source.is_relative_to(base):
            relative = source.relative_to(base)
            module_parts = [base.name, *relative.with_suffix("").parts]
            if module_parts and all(part != "__pycache__" and is_valid_module_part(part) for part in module_parts):
                candidates.append((base.parent, ".".join(module_parts)))

        candidates.append(base.parent)

    if source.is_relative_to(cwd):
        candidates.append(cwd)

    candidates.append(source.parent)

    seen: set[tuple[Path, str] | Path] = set()
    for candidate in candidates:
        if isinstance(candidate, tuple):
            import_root, module_name = candidate
            import_root = import_root.resolve()
            key = (import_root, module_name)
            if key in seen:
                continue
            seen.add(key)

            if not source.is_relative_to(import_root):
                continue

            return import_root, module_name

        import_root = candidate
        import_root = import_root.resolve()
        if import_root in seen:
            continue
        seen.add(import_root)

        if not source.is_relative_to(import_root):
            continue

        relative = source.relative_to(import_root)
        module_parts = list(relative.with_suffix("").parts)
        if not module_parts:
            continue
        if any(part == "__pycache__" or not is_valid_module_part(part) for part in module_parts):
            continue

        return import_root, ".".join(module_parts)

    return None


def clear_module_tree(root_module: str):
    prefix = f"{root_module}."
    for name in list(sys.modules):
        if name == root_module or name.startswith(prefix):
            sys.modules.pop(name, None)


def execute_module(source: Path, import_root: Path, module_name: str):
    original_sys_path = list(sys.path)
    try:
        sys.path.insert(0, str(import_root))
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            clear_module_tree(module_name.split(".", 1)[0])
            module = importlib.import_module(module_name)
            return vars(module)
    finally:
        sys.path[:] = original_sys_path


def execute_file(source: Path, import_root: Path):
    original_sys_path = list(sys.path)
    try:
        sys.path.insert(0, str(import_root))
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return runpy.run_path(str(source), run_name="__main__")
    finally:
        sys.path[:] = original_sys_path
