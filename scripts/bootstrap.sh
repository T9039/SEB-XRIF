#!/usr/bin/env bash
# Install everything needed for local development.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Installing Python dependencies with uv"
uv sync

echo "==> Installing pre-commit hooks"
uv run pre-commit install || true

if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env from .env.example"
fi

if command -v npm >/dev/null 2>&1; then
  echo "==> Installing web dependencies with npm"
  (cd web && npm install)
else
  echo "!! npm not found; skipping web install"
fi

echo "==> Bootstrap complete."
echo "    make api      # FastAPI on :8000"
echo "    make web      # Vite dev server on :5173"
echo "    make dev      # both at once"
echo "    make docker-up"
