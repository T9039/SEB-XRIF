#!/usr/bin/env bash
# Build and start the full stack (api, web, db, mlflow).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

docker compose up --build "$@"
