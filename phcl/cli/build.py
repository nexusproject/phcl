import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from phcl.core.registry import Registry
from phcl.render.hcl2 import build_hcl

from .config import DEFAULT_OUTPUT_EXTENSION, load_file_config, normalize_extension
from .loading import execute_file, execute_module, resolve_module_target
from .ui import Ansi, heading, paint, print_group_heading, print_result, status_word


@dataclass
class BuildResult:
    source: Path
    output: Optional[Path]
    status: str
    detail: str = ""


def discover_python_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]

    files = []
    for path in sorted(target.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return files


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


def compile_file(source: Path, *, base: Path, out_dir: Optional[Path], ext: Optional[str], stdout: bool) -> BuildResult:
    Registry.reset()
    current_module_name = None

    try:
        resolved = resolve_module_target(source, base)
        if resolved is not None:
            import_root, module_name = resolved
            current_module_name = module_name
            module_globals = execute_module(source, import_root, module_name)
        else:
            import_root = base if base.is_dir() else source.parent
            module_globals = execute_file(source, import_root)
            current_module_name = module_globals.get("__name__")
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

    registry = Registry.renderables(module_name=current_module_name)
    if not registry:
        Registry.reset()
        return BuildResult(source=source, output=None, status="skip", detail="registry is empty")

    output_ext = normalize_extension(ext) if ext else (file_config.extension or DEFAULT_OUTPUT_EXTENSION)

    rendered = build_hcl(registry, indent=file_config.indentation)
    Registry.reset()

    if stdout:
        import sys

        sys.stdout.write(rendered)
        return BuildResult(source=source, output=None, status="stdout")

    destination = output_path_for(source, base, out_dir, output_ext)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    return BuildResult(source=source, output=destination, status="write")


def command_build(args) -> int:
    started_at = time.perf_counter()
    target = Path(args.target).resolve()
    if not target.exists():
        import sys

        detail = paint("(path does not exist)", Ansi.dim, stream=sys.stderr)
        print(f"{heading('build failed', stream=sys.stderr)}", file=sys.stderr)
        print(f"  {status_word('fail', stream=sys.stderr)}  {target} {detail}", file=sys.stderr)
        return 1

    if args.stdout and target.is_dir():
        import sys

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
        import sys

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
