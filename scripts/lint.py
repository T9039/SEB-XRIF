#!/usr/bin/env python3
"""Lint and type-check the repository.

Runs on Windows, Linux, and macOS::

    uv run python scripts/lint.py
"""

from __future__ import annotations

from _common import ROOT, run


def main() -> int:
    print("==> ruff check")
    run(["uv", "run", "ruff", "check", "."])

    print("==> ruff format --check")
    run(["uv", "run", "ruff", "format", "--check", "."])

    print("==> mypy")
    run(["uv", "run", "mypy", "analytics", "api", "eval"])

    if (ROOT / "web" / "node_modules").is_dir():
        print("==> web check (Vite+: oxfmt + oxlint + typecheck)")
        run(["pnpm", "run", "lint"], cwd=ROOT / "web")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
