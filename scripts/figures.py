#!/usr/bin/env python3
"""Regenerate the documentation and paper figures.

The figure sources live in ``docs/figures/src`` and write their output next to
themselves, so each one runs from that directory. Works on Windows, Linux, and
macOS::

    uv run python scripts/figures.py
"""

from __future__ import annotations

from _common import ROOT, run

SCRIPTS = (
    "make_fig1_methods.py",
    "make_fig_lit_methods.py",
    "sebxrif_figs.py",
)


def main() -> int:
    figures = ROOT / "docs" / "figures"
    for name in SCRIPTS:
        code = run(["uv", "run", "python", f"src/{name}"], cwd=figures, check=False)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
