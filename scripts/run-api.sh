#!/usr/bin/env bash
# Run the FastAPI service with autoreload.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

exec uv run uvicorn api.main:app --reload --host 0.0.0.0 --port "${PORT:-8000}"
