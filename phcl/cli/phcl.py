import argparse
import importlib
import io
import os
import runpy
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from phcl.core.registry import Registry
from phcl.render.hcl2 import build_hcl

DEFAULT_OUTPUT_EXTENSION = ".hcl"


class Ansi:
    reset = "\033[0m"
    dim = "\033[2m"
    bold = "\033[1m"
    green = "\033[32m"
    yellow = "\033[33m"
    red = "\033[31m"
    cyan = "\033[36m"


NO_COLOR = False


def use_color(stream) -> bool:
    return bool(
        not NO_COLOR
        and getattr(stream, "isatty", lambda: False)()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM") != "dumb"
    )


def paint(text: str, *styles: str, stream=None) -> str:
    target = stream or sys.stdout
    if not use_color(target):
        return text
    return f"{''.join(styles)}{text}{Ansi.reset}"


def status_label(status: str, *, stream) -> str:
    labels = {
        "write": ("write", (Ansi.bold, Ansi.green)),
        "skip": ("skip", (Ansi.bold, Ansi.yellow)),
        "stdout": ("stdout", (Ansi.bold, Ansi.cyan)),
        "fail": ("fail", (Ansi.bold, Ansi.red)),
        "done": ("done", (Ansi.bold, Ansi.green)),
    }
    text, styles = labels.get(status, (status, (Ansi.bold,)))
    return f"{paint(text, *styles, stream=stream):<14}"


def heading(text: str, *, stream) -> str:
    marker = paint("==>", Ansi.bold, Ansi.cyan, stream=stream)
    return f"{marker} {paint(text, Ansi.bold, stream=stream)}"


def status_word(status: str, *, stream) -> str:
    words = {
        "write": "write",
        "skip": paint("skip", Ansi.dim, stream=stream),
        "stdout": paint("stdout", Ansi.dim, stream=stream),
        "fail": paint("fail", Ansi.red, stream=stream),
    }
    return words.get(status, paint(status, stream=stream))


@dataclass
class BuildResult:
    source: Path
    output: Optional[Path]
    status: str
    detail: str = ""


@dataclass(frozen=True)
class FileConfig:
    extension: Optional[str]
    indentation: str = "  "
    skip: bool = False


def discover_python_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]

    files = []
    for path in sorted(target.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return files


def normalize_extension(value: str) -> str:
    return value if value.startswith(".") else f".{value}"


def output_path_for(source: Path, base: Path, out_dir: Optional[Path], ext: str) -> Path:
    relative = source.relative_to(base)
    target = relative.with_suffix("")
    output_name = target.name

    if output_name.endswith(ext):
        destination_name = output_name
    else:
        destination_name = f"{output_name}{ext}"

    if out_dir is None:
        return source.parent / destination_name

    return out_dir / target.parent / destination_name


def load_file_config(module_globals: dict[str, Any]) -> Optional[FileConfig]:
    config = module_globals.get("PHCL")
    if config is None:
        return None

    extension = getattr(config, "extension", None)
    indentation = getattr(config, "indentation", "  ")
    skip = getattr(config, "skip", False)

    if extension is not None:
        extension = normalize_extension(extension)

    if not isinstance(indentation, str) or not indentation:
        raise TypeError("PHCL.indentation must be a non-empty string")

    return FileConfig(extension=extension, indentation=indentation, skip=bool(skip))


def is_valid_module_part(value: str) -> bool:
    return value.isidentifier()


def resolve_module_target(source: Path, base: Path) -> Optional[tuple[Path, str]]:
    source = source.resolve()
    base = base.resolve()
    candidates = []
    cwd = Path.cwd().resolve()

    if source.is_relative_to(cwd):
        candidates.append(cwd)

    if base.is_dir():
        candidates.append(base.parent)

    candidates.append(source.parent)

    seen: set[Path] = set()
    for import_root in candidates:
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


def compile_file(source: Path, *, base: Path, out_dir: Optional[Path], ext: Optional[str], stdout: bool) -> BuildResult:
    Registry.reset()

    try:
        resolved = resolve_module_target(source, base)
        if resolved is not None:
            import_root, module_name = resolved
            module_globals = execute_module(source, import_root, module_name)
        else:
            import_root = base if base.is_dir() else source.parent
            module_globals = execute_file(source, import_root)
    except Exception as exc:
        Registry.reset()
        return BuildResult(source=source, output=None, status="fail", detail=str(exc))

    try:
        file_config = load_file_config(module_globals)
    except Exception as exc:
        Registry.reset()
        return BuildResult(source=source, output=None, status="fail", detail=str(exc))

    if file_config is None:
        Registry.reset()
        return BuildResult(source=source, output=None, status="ignore")

    if file_config.skip:
        Registry.reset()
        return BuildResult(source=source, output=None, status="skip", detail="disabled")

    registry = Registry.renderables()
    if not registry:
        Registry.reset()
        return BuildResult(source=source, output=None, status="skip", detail="registry is empty")

    output_ext = normalize_extension(ext) if ext else (file_config.extension or DEFAULT_OUTPUT_EXTENSION)

    rendered = build_hcl(registry, indent=file_config.indentation)
    Registry.reset()

    if stdout:
        sys.stdout.write(rendered)
        return BuildResult(source=source, output=None, status="stdout")

    destination = output_path_for(source, base, out_dir, output_ext)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    return BuildResult(source=source, output=destination, status="write")


def print_result(result: BuildResult, root: Path):
    source = result.source.relative_to(root) if result.source.is_relative_to(root) else result.source

    if result.status == "write":
        output = result.output.relative_to(root) if result.output and result.output.is_relative_to(root) else result.output
        arrow = paint("->", Ansi.dim, stream=sys.stdout)
        print(f"  {status_word('write', stream=sys.stdout)} {source} {arrow} {output}")
    elif result.status == "skip":
        detail = paint(f"({result.detail})", Ansi.dim, stream=sys.stdout)
        print(f"  {status_word('skip', stream=sys.stdout)} {source} {detail}")
    elif result.status == "stdout":
        print(f"  {status_word('stdout', stream=sys.stderr)} {source}", file=sys.stderr)
    else:
        detail = paint(f"({result.detail})", Ansi.dim, stream=sys.stderr)
        print(f"  {status_word('fail', stream=sys.stderr)} {source} {detail}", file=sys.stderr)


def print_group_heading(label: str):
    print(heading(label, stream=sys.stdout), flush=True)


def command_build(args) -> int:
    started_at = time.perf_counter()
    target = Path(args.target).resolve()
    if not target.exists():
        detail = paint("(path does not exist)", Ansi.dim, stream=sys.stderr)
        print(f"{heading('build failed', stream=sys.stderr)}", file=sys.stderr)
        print(f"  {status_word('fail', stream=sys.stderr)}  {target} {detail}", file=sys.stderr)
        return 1

    if args.stdout and target.is_dir():
        print(f"{heading('build failed', stream=sys.stderr)}", file=sys.stderr)
        print(f"  {status_word('fail', stream=sys.stderr)}  --stdout can only be used with a single file target", file=sys.stderr)
        return 1

    base = target if target.is_dir() else target.parent
    out_dir = Path(args.out_dir).resolve() if args.out_dir else None

    if not args.stdout:
        target_label = str(target.relative_to(Path.cwd())) if target.is_relative_to(Path.cwd()) else str(target)
        print_group_heading(f"build {target_label}")

    results = []
    for source in discover_python_files(target):
        result = compile_file(
            source,
            base=base,
            out_dir=out_dir,
            ext=args.ext,
            stdout=args.stdout,
        )
        results.append(result)
        if args.stdout and result.status == "fail":
            print_result(result, Path.cwd())

    written = sum(result.status == "write" for result in results)
    skipped = sum(result.status == "skip" for result in results)
    failed = sum(result.status == "fail" for result in results)

    if not args.stdout:
        for result in results:
            if result.status == "ignore":
                continue
            if args.quiet and result.status != "fail":
                continue
            print_result(result, Path.cwd())

        elapsed = time.perf_counter() - started_at
        summary = paint(f"{written} written, {skipped} skipped, {failed} failed", Ansi.dim, stream=sys.stdout)
        print()
        print(heading(f"done in {elapsed:.2f}s", stream=sys.stdout))
        print(f"  {summary}")

    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phcl")
    subparsers = parser.add_subparsers(dest="command")

    build = subparsers.add_parser("build", help="Compile PHCL source files into HCL output")
    build.add_argument("target", help="Source file or directory to compile")
    build.add_argument("--out-dir", help="Write generated files into this directory")
    build.add_argument("--ext", help="Override output extension, for example .tf or .pkr.hcl")
    build.add_argument("--stdout", action="store_true", help="Write output to stdout instead of files")
    build.add_argument("--no-color", action="store_true", help="Disable ANSI colors in CLI output")
    build.add_argument("-q", "--quiet", action="store_true", help="Hide per-file write/skip output and show only failures plus summary")
    build.set_defaults(func=command_build)

    return parser


def main(argv=None) -> int:
    global NO_COLOR
    parser = build_parser()
    args = parser.parse_args(argv)
    NO_COLOR = bool(getattr(args, "no_color", False))

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
