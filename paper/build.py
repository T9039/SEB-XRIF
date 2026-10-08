#!/usr/bin/env python3
"""Build the SEB-XRIF paper PDF.

Markdown in ``sections/*.md`` is the source of truth. This script regenerates
the data tables from ``reports/`` (stdlib Python only), then compiles with Typst
(``cmarker`` renders the Markdown). The comparison figure is embedded by
``main.typ`` from ``../reports/figures/``.

Works on Windows, Linux, and macOS::

    uv run python paper/build.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    tables = HERE / "tools" / "make_tables.py"
    if tables.is_file():
        subprocess.run([sys.executable, str(tables)], cwd=HERE, check=False)
    else:
        print("!! make_tables.py not found; leaving generated tables as they are")

    if shutil.which("typst") is None:
        print("!! typst not found. Install it from https://typst.app")
        return 1

    subprocess.run(
        ["typst", "compile", "--root", "..", "main.typ", "main.pdf"],
        cwd=HERE,
        check=True,
    )
    print(f"==> Wrote {HERE / 'main.pdf'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
