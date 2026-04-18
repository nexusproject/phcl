import os
import sys
from pathlib import Path


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


def print_result(result, root: Path):
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
