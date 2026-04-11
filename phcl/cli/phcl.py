import argparse
import io
import runpy
import sys
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from phcl.core.registry import Registry
from phcl.render.hcl2 import build_hcl


@dataclass
class BuildResult:
    source: Path
    output: Optional[Path]
    status: str
    detail: str = ""


def infer_output_extension(source: Path) -> Optional[str]:
    suffixes = source.suffixes
    if not suffixes or suffixes[-1] != ".py":
        return None

    inferred = "".join(suffixes[:-1])
    return inferred or None


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

    while target.suffix:
        target = target.with_suffix("")

    if out_dir is None:
        return source.parent / f"{target.name}{ext}"

    return out_dir / target.parent / f"{target.name}{ext}"


def execute_file(source: Path, import_root: Path):
    original_sys_path = list(sys.path)
    try:
        sys.path.insert(0, str(import_root))
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            runpy.run_path(str(source), run_name="__main__")
    finally:
        sys.path[:] = original_sys_path


def compile_file(source: Path, *, base: Path, out_dir: Optional[Path], ext: Optional[str], stdout: bool) -> BuildResult:
    Registry.reset()

    import_root = base if base.is_dir() else source.parent

    try:
        execute_file(source, import_root)
    except Exception as exc:
        Registry.reset()
        return BuildResult(source=source, output=None, status="fail", detail=str(exc))

    registry = Registry.renderables()
    if not registry:
        Registry.reset()
        return BuildResult(source=source, output=None, status="skip", detail="registry is empty")

    output_ext = ext or infer_output_extension(source)
    if not output_ext:
        Registry.reset()
        return BuildResult(
            source=source,
            output=None,
            status="fail",
            detail="cannot infer output extension; pass --ext explicitly",
        )

    rendered = build_hcl(registry)
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
        print(f"write  {source} -> {output}")
    elif result.status == "skip":
        print(f"skip   {source} ({result.detail})")
    elif result.status == "stdout":
        print(f"stdout {source}", file=sys.stderr)
    else:
        print(f"fail   {source} ({result.detail})", file=sys.stderr)


def command_build(args) -> int:
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"fail   {target} (path does not exist)", file=sys.stderr)
        return 1

    if args.stdout and target.is_dir():
        print("fail   --stdout can only be used with a single file target", file=sys.stderr)
        return 1

    base = target if target.is_dir() else target.parent
    out_dir = Path(args.out_dir).resolve() if args.out_dir else None

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
        if args.stdout:
            if result.status != "stdout":
                print_result(result, Path.cwd())
        else:
            print_result(result, Path.cwd())

    written = sum(result.status == "write" for result in results)
    skipped = sum(result.status == "skip" for result in results)
    failed = sum(result.status == "fail" for result in results)

    if not args.stdout:
        print(f"done   {written} written, {skipped} skipped, {failed} failed")

    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phcl")
    subparsers = parser.add_subparsers(dest="command")

    build = subparsers.add_parser("build", help="Compile PHCL source files into HCL output")
    build.add_argument("target", help="Source file or directory to compile")
    build.add_argument("--out-dir", help="Write generated files into this directory")
    build.add_argument("--ext", help="Override output extension, for example .tf or .pkr.hcl")
    build.add_argument("--stdout", action="store_true", help="Write output to stdout instead of files")
    build.set_defaults(func=command_build)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
