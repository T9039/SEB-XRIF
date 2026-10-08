#!/usr/bin/env python3
"""Run Storybook for the ui component library.

Installs the workspace dependencies first if they are missing. Works on
Windows, Linux, and macOS::

    uv run python scripts/storybook.py
"""

from __future__ import annotations

import sys

from _common import ROOT, need, run


def main() -> int:
    need("pnpm", "Enable it with: corepack enable   (or: npm i -g pnpm)")

    ui = ROOT / "ui"
    if not (ui / "node_modules").is_dir():
        print("==> Installing workspace dependencies with pnpm")
        run(["pnpm", "install"])

    return run(["pnpm", "storybook", *sys.argv[1:]], cwd=ui)


if __name__ == "__main__":
    raise SystemExit(main())
