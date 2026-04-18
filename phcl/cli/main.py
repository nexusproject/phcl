import argparse

from .build import command_build
from .ui import NO_COLOR
from phcl.core import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phcl")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
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
    parser = build_parser()
    args = parser.parse_args(argv)

    import phcl.cli.ui as ui

    ui.NO_COLOR = bool(getattr(args, "no_color", False))

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)
