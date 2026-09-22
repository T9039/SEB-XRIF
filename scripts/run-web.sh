#!/usr/bin/env bash
# Run the Vite+ dev server for the dashboard.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/web"

exec pnpm run dev
