#!/usr/bin/env bash
# Build the SEB-XRIF paper PDF.
#
# Markdown in sections/*.md is the source of truth. This script regenerates the
# data tables from reports/ (stdlib Python only), then compiles with Typst
# (cmarker renders the Markdown). The comparison figure is embedded by main.typ
# from ../reports/figures/.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if command -v python3 >/dev/null 2>&1; then
  python3 tools/make_tables.py
else
  echo "!! python3 not found; leaving generated tables as they are"
fi

if ! command -v typst >/dev/null 2>&1; then
  echo "!! typst not found. Install it from https://typst.app"
  exit 1
fi

typst compile --root .. main.typ main.pdf
echo "==> Wrote $(pwd)/main.pdf"
