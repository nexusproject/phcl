import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from phcl.core.registry import Registry
from phcl.render.hcl2 import build_hcl
from phcl.runtime import _reset_build_target, _set_build_target

from .config import DEFAULT_OUTPUT_EXTENSION, load_file_config, normalize_extension
from .loading import execute_file, execute_module, resolve_module_target
from .ui import Ansi, heading, paint, print_group_heading, print_result, status_word


@dataclass
class BuildWarning:
    message: str
    filename: str
    lineno: int


@dataclass
class BuildResult:
    source: Path
    output: Optional[Path]
    status: str
    detail: str = ""
    warnings: Optional[list[BuildWarning]] = None


def collect_build_warnings(records) -> list[BuildWarning]:
    return [
        BuildWarning(
            message=str(record.message),
            filename=record.filename,
            lineno=record.lineno,
        )
        for record in records
        if issubclass(record.category, DeprecationWarning)
    ]


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
    target_token = _set_build_target(base)
    try:
        with warnings.catch_warnings(record=True) as warning_records:
            warnings.simplefilter("always", DeprecationWarning)

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
                return BuildResult(
                    source=source,
                    output=None,
                    status="fail",
                    detail=str(exc),
                    warnings=collect_build_warnings(warning_records),
                )

            try:
                file_config = load_file_config(module_globals)
            except Exception as exc:
                Registry.reset()
                return BuildResult(
                    source=source,
                    output=None,
                    status="fail",
                    detail=str(exc),
                    warnings=collect_build_warnings(warning_records),
                )

            if file_config is None:
                Registry.reset()
                return BuildResult(
                    source=source,
                    output=None,
                    status="ignore",
                    warnings=collect_build_warnings(warning_records),
                )

            if file_config.skip:
                Registry.reset()
                return BuildResult(
                    source=source,
                    output=None,
                    status="skip",
                    detail="disabled",
                    warnings=collect_build_warnings(warning_records),
                )

            registry = Registry.renderables(module_name=current_module_name)
            if not registry:
                Registry.reset()
                return BuildResult(
                    source=source,
                    output=None,
                    status="skip",
                    detail="registry is empty",
                    warnings=collect_build_warnings(warning_records),
                )

            output_ext = normalize_extension(ext) if ext else (file_config.extension or DEFAULT_OUTPUT_EXTENSION)

            rendered = build_hcl(registry, indent=file_config.indentation)
            Registry.reset()

            if stdout:
                import sys

                sys.stdout.write(rendered)
                return BuildResult(
                    source=source,
                    output=None,
                    status="stdout",
                    warnings=collect_build_warnings(warning_records),
                )

            destination = output_path_for(source, base, out_dir, output_ext)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered, encoding="utf-8")
            return BuildResult(
                source=source,
                output=destination,
                status="write",
                warnings=collect_build_warnings(warning_records),
            )
    finally:
        _reset_build_target(target_token)


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
    seen_warnings = set()
    for source in discover_python_files(target):
        result = compile_file(
            source,
            base=base,
            out_dir=out_dir,
            ext=args.ext,
            stdout=args.stdout,
        )
        unique_warnings = []
        for warning in result.warnings or []:
            key = (warning.filename, warning.lineno, warning.message)
            if key in seen_warnings:
                continue
            seen_warnings.add(key)
            unique_warnings.append(warning)
        result.warnings = unique_warnings

        results.append(result)
        if args.stdout and (result.status == "fail" or result.warnings):
            print_result(result, Path.cwd())

    written = sum(result.status == "write" for result in results)
    skipped = sum(result.status == "skip" for result in results)
    failed = sum(result.status == "fail" for result in results)
    warning_count = sum(len(result.warnings or []) for result in results)

    if not args.stdout:
        import sys

        for result in results:
            if result.status == "ignore" and not result.warnings:
                continue
            if args.quiet and result.status != "fail":
                continue
            print_result(result, Path.cwd())

        elapsed = time.perf_counter() - started_at
        summary_parts = [f"{written} written", f"{skipped} skipped", f"{failed} failed"]
        if warning_count:
            summary_parts.append(f"{warning_count} warnings")
        summary = paint(", ".join(summary_parts), Ansi.dim, stream=sys.stdout)
        print()
        print(heading(f"done in {elapsed:.2f}s", stream=sys.stdout))
        print(f"  {summary}")

    return 1 if failed else 0
