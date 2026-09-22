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

if ! command -v pnpm >/dev/null 2>&1; then
  echo "!! pnpm not found. Install it with: corepack enable  (or npm i -g pnpm)"
  exit 1
fi

echo "==> Installing JavaScript workspace dependencies (web + ui) with pnpm"
pnpm install

echo "==> Bootstrap complete."
echo "    make api       # FastAPI on :8000"
echo "    make web       # Vite+ dev server on :5173"
echo "    make dev       # both at once"
echo "    make storybook # component library on :6006"
echo "    make docker-up"
