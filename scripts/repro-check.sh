#!/usr/bin/env bash
# Verify the framework reproduces from a clean checkout.
#
# Copies the tracked tree (working-tree contents, so uncommitted edits are
# included) into a temporary directory with no DVC cache, re-runs the pipeline
# there, and fails if the regenerated dvc.lock differs from the committed one.
# A difference means the recorded data/model artifacts no longer match the
# sources that are supposed to produce them.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f dvc.lock ]]; then
  echo "!! No dvc.lock found at the repo root." >&2
  exit 2
fi

work="$(mktemp -d)"
lock_before="$(mktemp)"
cleanup() { rm -rf "$work" "$lock_before"; }
trap cleanup EXIT

echo "==> Exporting the tracked tree to $work"
git ls-files -z | tar --null -T - -cf - | tar -x -C "$work"
cp dvc.lock "$lock_before"

# DVC needs an SCM context; give the export a throwaway local history.
git -C "$work" init -q
git -C "$work" -c user.email=repro-check@localhost -c user.name=repro-check \
  add -A
git -C "$work" -c user.email=repro-check@localhost -c user.name=repro-check \
  commit -qm "repro-check export"

echo "==> Reproducing the pipeline from a clean checkout"
cd "$work"
UV_PROJECT="$work" UV_PROJECT_ENVIRONMENT="$ROOT/.venv" \
  uv run --frozen dvc repro

echo "==> Comparing the regenerated lock to the committed lock"
if diff -u "$lock_before" dvc.lock; then
  echo "==> Reproducible: the regenerated dvc.lock matches the committed graph"
else
  echo "!! Reproduction drifted from the committed lock (diff above)." >&2
  echo "   Run 'uv run dvc repro' in the repo root and commit dvc.lock." >&2
  exit 1
fi
