"""Shared helpers for SEB-XRIF's cross-platform task scripts.

These scripts are the single implementation behind the ``make`` targets, so
there is no separate shell/``.cmd`` script per platform::

    uv run python scripts/<task>.py

Everything here is standard library only and runs on Windows, Linux, and macOS.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = os.name == "nt"

THREAD_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


def need(name: str, hint: str | None = None) -> None:
    """Exit with a helpful message when an executable is not on ``PATH``."""
    if shutil.which(name) is None:
        message = f"!! '{name}' is not installed."
        if hint:
            message += f" {hint}"
        print(message, file=sys.stderr)
        raise SystemExit(1)


def wrap(cmd: list[str]) -> list[str]:
    """Resolve the executable, routing Windows ``.cmd``/``.bat`` shims via cmd.exe."""
    exe = shutil.which(cmd[0])
    if not exe:
        return cmd
    if IS_WINDOWS and exe.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", exe, *cmd[1:]]
    return [exe, *cmd[1:]]


def run(cmd: list[str], *, cwd: Path = ROOT, check: bool = True) -> int:
    """Print and run ``cmd`` from ``cwd``; raise ``SystemExit`` on failure."""
    if shutil.which(cmd[0]) is None:
        print(
            f"!! '{cmd[0]}' is not installed. "
            "See the Prerequisites section of README.md.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"==> {' '.join(cmd)}")
    code = subprocess.run(wrap(cmd), cwd=str(cwd)).returncode
    if code and check:
        raise SystemExit(code)
    return code


def pin_threads() -> None:
    """Pin native math threads; the Python layer is single-threaded by config."""
    for name in THREAD_VARS:
        os.environ.setdefault(name, "1")
