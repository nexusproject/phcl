"""
Python-side runtime helpers for PHCL authoring.

These helpers execute during PHCL generation/build time rather than being
rendered as HCL expressions in the output.
"""

from __future__ import annotations

import inspect
from pathlib import Path


def path_module() -> Path:
    """
    Return the directory of the calling PHCL source module as a ``Path``.

    This is a Python-side runtime helper analogous in spirit to Terraform's
    ``path.module``, but it resolves against the caller's source file during
    PHCL generation.
    """

    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        raise RuntimeError("path_module() could not resolve the calling frame")

    caller_globals = frame.f_back.f_globals
    caller_file = caller_globals.get("__file__")
    if not caller_file:
        raise RuntimeError("path_module() requires the calling module to define __file__")

    return Path(caller_file).resolve().parent


__all__ = ["path_module"]
