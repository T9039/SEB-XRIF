#!/usr/bin/env python3
"""Remove caches and build artifacts.

Works on Windows, Linux, and macOS (no ``find``/``rm`` required)::

    uv run python scripts/clean.py
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from _common import ROOT

PRUNE = {".git", ".venv", "node_modules", ".dvc", ".ruff_cache"}
TARGETS = (".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov", ".coverage")


def main() -> int:
    for dirpath, dirnames, _ in os.walk(ROOT, topdown=True):
        dirnames[:] = [name for name in dirnames if name not in PRUNE]
        if Path(dirpath).name == "__pycache__":
            shutil.rmtree(dirpath, ignore_errors=True)
            dirnames[:] = []

    for name in TARGETS:
        path = ROOT / name
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink(missing_ok=True)

    print("==> Removed caches and build artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
