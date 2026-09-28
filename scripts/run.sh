#!/usr/bin/env bash
# Bring the whole SEB-XRIF infrastructure up for a local session.
#
# One command, idempotent and safe to re-run:
#   1. installs dependencies if they are missing (delegates to bootstrap.sh)
#   2. creates .env from .env.example if absent
#   3. trains the default model if no artifact exists yet
#   4. starts the API (:8000) and the dashboard (:5173) together
#
# Usage:
#   ./scripts/run.sh            # api + dashboard
#   ./scripts/run.sh --no-train # skip the training step
#   PORT=9000 ./scripts/run.sh  # API port (dashboard stays on 5173)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TRAIN=1
for arg in "$@"; do
  case "$arg" in
    --no-train) TRAIN=0 ;;
    -h|--help)
      sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
  esac
done

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "!! '$1' is not installed. See the Prerequisites section of README.md." >&2
    exit 1
  }
}

port_busy() {
  # Returns 0 (busy) if something already answers on the port.
  if command -v curl >/dev/null 2>&1; then
    curl -s -o /dev/null --max-time 2 "http://localhost:$1/" 2>/dev/null
  else
    return 1
  fi
}

echo "==> Checking prerequisites"
need uv
need node
need pnpm

# Fail clearly if the dev ports are already taken, rather than silently
# shifting to another port (Vite would move the dashboard to 5174).
for port in 5173 "${PORT:-8000}"; do
  if port_busy "$port"; then
    echo "!! Port $port is already in use." >&2
    echo "   Stop the process using it (or set PORT=... for the API) and retry." >&2
    exit 1
  fi
done


# 1. Dependencies.
if [ ! -d .venv ] || [ ! -d node_modules ]; then
  echo "==> Missing dependencies; running bootstrap"
  ./scripts/bootstrap.sh
fi

# 2. Environment file.
if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env from .env.example"
fi

# 3. Model artifact (the dashboard is much more useful with one).
if [ "$TRAIN" = "1" ] && [ ! -f models/model.joblib ]; then
  echo "==> No model found; training the default Random Forest"
  uv run python -m analytics.train --no-mlflow
fi

# 4. Run both servers.
PORT="${PORT:-8000}"
echo
echo "=============================================================="
echo " SEB-XRIF is starting"
echo "   Dashboard : http://localhost:5173"
echo "   API docs  : http://localhost:${PORT}/docs"
echo "   Stop      : Ctrl+C"
echo "=============================================================="
echo

cleanup() {
  trap - EXIT INT TERM
  kill 0 2>/dev/null || true
}
trap cleanup EXIT INT TERM

uv run uvicorn api.main:app --reload --host 0.0.0.0 --port "$PORT" &
(cd "$ROOT/web" && pnpm run dev) &

wait
