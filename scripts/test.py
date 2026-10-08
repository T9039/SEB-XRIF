#!/usr/bin/env python3
"""Run the Python test suite with coverage.

Arguments are passed through to pytest::

    uv run python scripts/test.py -k xapi
"""

from __future__ import annotations

import sys

from _common import run

COVERAGE = ["--cov=analytics", "--cov=api", "--cov=eval", "--cov-report=term-missing"]


def main() -> int:
    return run(["uv", "run", "pytest", *COVERAGE, *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
