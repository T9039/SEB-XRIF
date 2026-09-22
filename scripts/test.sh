#!/usr/bin/env bash
# Run the Python test suite with coverage.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

exec uv run pytest --cov=analytics --cov=api --cov=eval --cov-report=term-missing "$@"
