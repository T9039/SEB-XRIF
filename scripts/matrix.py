#!/usr/bin/env python3
"""Run the full SEB-XRIF model comparison matrix.

Threads are pinned to one by default so the matrix cannot oversubscribe a small
machine (nested estimator/CV worker pools were the culprit before). Override
with ``N_JOBS`` / ``OMP_NUM_THREADS`` if you know what you are doing::

    uv run python scripts/matrix.py            # same as --all
    uv run python scripts/matrix.py --models svc knn
"""

from __future__ import annotations

import sys

from _common import pin_threads, run


def main() -> int:
    pin_threads()
    args = sys.argv[1:] or ["--all"]
    return run(["uv", "run", "python", "-m", "analytics.benchmark", *args])


if __name__ == "__main__":
    raise SystemExit(main())
