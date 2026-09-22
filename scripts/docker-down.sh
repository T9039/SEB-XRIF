#!/usr/bin/env bash
# Stop the stack and remove containers.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

docker compose down "$@"
