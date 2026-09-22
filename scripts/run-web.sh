#!/usr/bin/env bash
# Run the Vite dev server.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/web"

exec npm run dev
