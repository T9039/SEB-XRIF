#!/usr/bin/env bash
# Run Storybook for the ui component library.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/ui"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "!! pnpm not found. Install it with: corepack enable  (or npm i -g pnpm)"
  exit 1
fi

if [ ! -d node_modules ]; then
  echo "==> Installing ui dependencies with pnpm"
  pnpm install
fi

exec pnpm storybook "$@"
