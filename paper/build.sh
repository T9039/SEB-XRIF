#!/usr/bin/env bash
# Build the SEB-XRIF paper PDF.
#
# Markdown in sections/*.md is the source of truth; this script refreshes the
# generated results table from reports/, then compiles with Typst (cmarker
# renders the Markdown). The comparison figure is embedded by main.typ from
# ../reports/figures/.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if [ -f ../reports/results.md ]; then
  cp ../reports/results.md sections/results_table.md
  echo "==> Refreshed sections/results_table.md from reports/results.md"
else
  printf '_Results table not generated yet. Run `make matrix` first._\n' \
    > sections/results_table.md
  echo "!! reports/results.md not found; wrote a placeholder"
fi

if ! command -v typst >/dev/null 2>&1; then
  echo "!! typst not found. Install it from https://typst.app"
  exit 1
fi

typst compile --root .. main.typ main.pdf
echo "==> Wrote $(pwd)/main.pdf"
