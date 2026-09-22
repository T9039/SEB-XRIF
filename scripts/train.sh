#!/usr/bin/env bash
# Train models. Passes all arguments through to analytics.train.
#   ./scripts/train.sh
#   ./scripts/train.sh --all
#   ./scripts/train.sh --models random_forest svc knn
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Pin native math threads; the Python layer is single-threaded by config.
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"

exec uv run python -m analytics.train "$@"
