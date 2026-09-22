#!/usr/bin/env bash
# Lint and type-check the repository.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> ruff check"
uv run ruff check .

echo "==> ruff format --check"
uv run ruff format --check .

echo "==> mypy"
uv run mypy analytics api eval

if [ -d web/node_modules ]; then
  echo "==> web check (Vite+: oxfmt + oxlint + typecheck)"
  (cd web && npm run lint)
fi
