#!/usr/bin/env python3
"""Tune the top models with Optuna.

Arguments are passed through to ``analytics.tune``::

    uv run python scripts/tune.py --trials 20
"""

from __future__ import annotations

import sys

from _common import pin_threads, run


def main() -> int:
    pin_threads()
    return run(["uv", "run", "python", "-m", "analytics.tune", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
