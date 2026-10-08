#!/usr/bin/env python3
"""Run the Vite+ dev server for the dashboard.

Works on Windows, Linux, and macOS::

    uv run python scripts/run_web.py
"""

from __future__ import annotations

import json

from _common import ROOT, run


def web_cmd() -> list[str]:
    """Mirror web/package.json's "dev" script through ``pnpm exec``.

    ``pnpm exec`` runs the binary directly instead of through pnpm's lifecycle
    wrapper, which avoids the "[ELIFECYCLE] Command failed." noise pnpm prints
    when the dev server is stopped by a signal.
    """
    script = "vp dev"
    try:
        pkg = json.loads((ROOT / "web" / "package.json").read_text(encoding="utf-8"))
        script = pkg.get("scripts", {}).get("dev", script)
    except Exception:
        pass
    return ["pnpm", "exec", *script.split()]


def main() -> int:
    return run(web_cmd(), cwd=ROOT / "web")


if __name__ == "__main__":
    raise SystemExit(main())
