#!/usr/bin/env python3
"""Train models. Passes all arguments through to ``analytics.train``.

Examples::

    uv run python scripts/train.py
    uv run python scripts/train.py --all
    uv run python scripts/train.py --models random_forest svc knn
"""

from __future__ import annotations

import sys

from _common import pin_threads, run


def main() -> int:
    pin_threads()
    return run(["uv", "run", "python", "-m", "analytics.train", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
