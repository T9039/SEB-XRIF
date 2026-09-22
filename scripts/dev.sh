#!/usr/bin/env bash
# Run the API and the web dev server together.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cleanup() {
  trap - EXIT INT TERM
  kill 0 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> Starting API on http://localhost:8000"
uv run uvicorn api.main:app --reload --port 8000 &

echo "==> Starting web dev server on http://localhost:5173"
(cd "$ROOT/web" && pnpm run dev) &

wait
