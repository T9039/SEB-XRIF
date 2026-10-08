#!/usr/bin/env python3
"""Install everything needed for local development.

Safe to re-run, and identical on Windows, Linux, and macOS (no Git Bash
required)::

    uv run python scripts/bootstrap.py
"""

from __future__ import annotations

import shutil

from _common import ROOT, need, run


def main() -> int:
    need("uv", "Install it from https://docs.astral.sh/uv/ (it manages Python 3.12).")
    need("node", "Install Node.js 20+.")
    need("pnpm", "Enable it with: corepack enable   (or: npm install -g pnpm)")

    print("==> Installing Python dependencies with uv")
    run(["uv", "sync"])

    print("==> Installing pre-commit hooks")
    run(["uv", "run", "pre-commit", "install"], check=False)

    env = ROOT / ".env"
    if not env.exists():
        shutil.copy(ROOT / ".env.example", env)
        print("==> Created .env from .env.example")

    print("==> Installing JavaScript workspace dependencies (web + ui) with pnpm")
    run(["pnpm", "install"])

    print()
    print("==> Bootstrap complete.")
    print(
        "    make up        # install if needed, train if needed, run api + dashboard"
    )
    print("    make api       # FastAPI on :8000")
    print("    make web       # Vite+ dev server on :5173")
    print("    make dev       # both at once (no training step)")
    print("    make storybook # component library on :6006")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
