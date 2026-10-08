#!/usr/bin/env python3
"""Run the FastAPI service with autoreload.

Respects the ``PORT`` environment variable (default 8000). Works on Windows,
Linux, and macOS::

    uv run python scripts/run_api.py
    PORT=9000 uv run python scripts/run_api.py
"""

from __future__ import annotations

import os

from _common import run


def main() -> int:
    port = os.environ.get("PORT", "8000")
    return run(
        [
            "uv",
            "run",
            "uvicorn",
            "api.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            port,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
