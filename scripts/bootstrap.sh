#!/usr/bin/env bash
# Install everything needed for local development.
# Safe to re-run. On Windows use Git Bash (see README, "Windows setup").
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "!! 'uv' is not installed." >&2
  echo "   Install it from https://docs.astral.sh/uv/ (it manages Python 3.12)." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "!! 'node' is not installed. Install Node.js 20+." >&2
  exit 1
fi

if ! command -v pnpm >/dev/null 2>&1; then
  echo "!! 'pnpm' is not installed." >&2
  echo "   Enable it with: corepack enable   (or: npm install -g pnpm)" >&2
  exit 1
fi

echo "==> Installing Python dependencies with uv"
uv sync

echo "==> Installing pre-commit hooks"
uv run pre-commit install || echo "   (pre-commit skipped; not required to run the app)"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env from .env.example"
fi

echo "==> Installing JavaScript workspace dependencies (web + ui) with pnpm"
pnpm install

echo
echo "==> Bootstrap complete."
echo "    make up        # install if needed, train if needed, run api + dashboard"
echo "    make api       # FastAPI on :8000"
echo "    make web       # Vite+ dev server on :5173"
echo "    make dev       # both at once (no training step)"
echo "    make storybook # component library on :6006"
