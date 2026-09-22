#!/usr/bin/env bash
# Train models. Passes all arguments through to analytics.train.
#   ./scripts/train.sh
#   ./scripts/train.sh --all
#   ./scripts/train.sh --models random_forest svc knn
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

exec uv run python -m analytics.train "$@"
