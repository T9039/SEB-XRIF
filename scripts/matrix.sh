#!/usr/bin/env bash
# Run the full SEB-XRIF model comparison matrix.
#
# Threads are pinned to one by default so the matrix cannot oversubscribe a
# small machine (nested estimator/CV worker pools were the culprit before).
# Override with N_JOBS / OMP_NUM_THREADS if you know what you are doing.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"

ARGS=("$@")
if [ "$#" -eq 0 ]; then
  ARGS=(--all)
fi

exec uv run python -m analytics.benchmark "${ARGS[@]}"
