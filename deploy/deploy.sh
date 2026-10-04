#!/usr/bin/env bash
# Deploy the SEB-XRIF beta stack on this host and expose it through
# Tailscale Funnel on public port 8443 (override with FUNNEL_PORT). 8443 is a
# standard HTTPS-alt port; port 10000 is filtered by many networks.
#
#   ./deploy/deploy.sh
#
# Idempotent: safe to re-run. Secrets are generated once into deploy/.env and
# deploy/Caddyfile (both gitignored); delete them to rotate the credentials.
#
# Nothing is published to the host except Caddy, bound to 127.0.0.1. Funnel is
# the only path from the public internet, and it reaches exactly one port.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_DIR="$ROOT/deploy"
ENV_FILE="$DEPLOY_DIR/.env"
CADDYFILE="$DEPLOY_DIR/Caddyfile"
COMPOSE=(docker compose -f "$DEPLOY_DIR/docker-compose.yml" --env-file "$ENV_FILE")

FUNNEL_PORT="${FUNNEL_PORT:-8443}"
CADDY_PORT="${CADDY_PORT:-9080}"

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "!! '$1' is not installed." >&2; exit 1; }
}
need docker
need tailscale
need openssl

# 1. Secrets, generated once.
if [ ! -f "$ENV_FILE" ]; then
  echo "==> Generating deploy/.env"
  PG_PW="$(openssl rand -hex 16)"
  BETA_PW="$(openssl rand -base64 18 | tr -dc 'A-Za-z0-9' | cut -c1-16)"
  cat > "$ENV_FILE" <<EOF
POSTGRES_PASSWORD=$PG_PW
CADDY_PORT=$CADDY_PORT
BETA_USER=beta
BETA_PASSWORD=$BETA_PW
EOF
  chmod 600 "$ENV_FILE"
fi
# shellcheck disable=SC1090
set -a; . "$ENV_FILE"; set +a

# 2. Caddyfile with the bcrypt hash of the beta password.
if [ ! -f "$CADDYFILE" ]; then
  echo "==> Generating deploy/Caddyfile"
  HASH="$(docker run --rm caddy:2-alpine caddy hash-password --plaintext "$BETA_PASSWORD" | tail -1)"
  sed "s|__BASIC_AUTH__|${BETA_USER} ${HASH}|" \
    "$DEPLOY_DIR/Caddyfile.template" > "$CADDYFILE"
fi

# 3. Build and start.
echo "==> Building and starting the stack (first build can take a few minutes)"
"${COMPOSE[@]}" up -d --build

# 4. Wait for the API to report a loaded model.
echo "==> Waiting for the API"
ready=0
for _ in $(seq 1 60); do
  if "${COMPOSE[@]}" exec -T api python -c \
      "import json,urllib.request; exit(0 if json.load(urllib.request.urlopen('http://localhost:8000/health')).get('model_loaded') else 1)" \
      >/dev/null 2>&1; then
    ready=1; break
  fi
  sleep 2
done
if [ "$ready" != 1 ]; then
  echo "!! API did not become ready with a model loaded." >&2
  echo "   Check: ${COMPOSE[*]} logs api" >&2
  exit 1
fi
echo "    API ready (model loaded)"

# 5. Expose through Funnel.
echo "==> Exposing through Tailscale Funnel on :$FUNNEL_PORT"
if ! tailscale funnel --bg --yes --https="$FUNNEL_PORT" "http://127.0.0.1:${CADDY_PORT}"; then
  echo "!! Could not configure Funnel automatically." >&2
  echo "   Enable Funnel for this tailnet (admin console > Access controls >" >&2
  echo "   Tailnet policy file, or the first-run approval prompt), then re-run." >&2
  exit 1
fi

DNS="$(tailscale status --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["Self"]["DNSName"].rstrip("."))')"

echo
echo "=============================================================="
echo " SEB-XRIF beta is live"
echo "   URL      : https://${DNS}:${FUNNEL_PORT}"
echo "   Username : ${BETA_USER}"
echo "   Password : ${BETA_PASSWORD}"
echo
echo "   Stop the funnel : tailscale funnel --https=${FUNNEL_PORT} off"
echo "   Stop the stack  : ${COMPOSE[*]} down"
echo "=============================================================="
