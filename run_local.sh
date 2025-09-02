#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "Error: wrangler is not installed. Run ./setup.sh first." >&2
  exit 1
fi
WRANGLER_CMD="wrangler"

# Check for OpenAI API key in environment
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "Error: OPENAI_API_KEY environment variable is not set." >&2
  echo "Please set it with: export OPENAI_API_KEY='your-api-key-here'" >&2
  exit 1
fi

echo "Using OPENAI_API_KEY from environment (${#OPENAI_API_KEY} characters)"

# Ensure .dev.vars exists so Wrangler binds OPENAI_API_KEY into env
DEV_VARS_FILE="$SCRIPT_DIR/.dev.vars"
{
  echo "OPENAI_API_KEY=$OPENAI_API_KEY"
} > "$DEV_VARS_FILE"
echo ".dev.vars written with OPENAI_API_KEY binding"

PORT=${PORT:-8787}

# Start wrangler dev in the background with environment variables and explicit var binding
# No log files; stream logs directly to console
OPENAI_API_KEY="$OPENAI_API_KEY" \
$WRANGLER_CMD dev --port $PORT --local --config "$SCRIPT_DIR/wrangler.jsonc" \
  --var OPENAI_API_KEY:$OPENAI_API_KEY &
WRANGLER_PID=$!

# Fallback if the above PID capture fails due to shell quirks
if [ -z "${WRANGLER_PID:-}" ]; then
  WRANGLER_PID=$(pgrep -f "wrangler dev --port $PORT --local --config $SCRIPT_DIR/wrangler.jsonc" | head -n1 || true)
fi

cleanup() {
  if [ -n "${WRANGLER_PID:-}" ] && kill -0 "$WRANGLER_PID" >/dev/null 2>&1; then
    kill "$WRANGLER_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

# Wait until server is ready
ATTEMPTS=40
until curl -sS "http://127.0.0.1:$PORT" >/dev/null 2>&1; do
  ATTEMPTS=$((ATTEMPTS - 1))
  if [ $ATTEMPTS -le 0 ]; then
    echo "wrangler dev did not become ready in time." >&2
    exit 1
  fi
  sleep 0.25
done

echo "Local dev server is running on http://127.0.0.1:$PORT"
RESPONSE=$(curl -sS -H 'accept: application/json' "http://127.0.0.1:$PORT") || true

echo "Response:"
echo "$RESPONSE"

if echo "$RESPONSE" | grep -q '"ok": *true'; then
  echo "Local smoke test passed. Logs streaming below (Ctrl+C to stop)."
else
  echo "Local smoke test failed: expected to find '"ok": true' in the response." >&2
  exit 1
fi

# Keep process attached to show logs
wait "$WRANGLER_PID" 2>/dev/null || true 