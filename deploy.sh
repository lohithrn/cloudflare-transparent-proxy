#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "Error: wrangler is not installed. Run ./setup.sh first." >&2
  exit 1
fi
WRANGLER_CMD="wrangler"

# Check for required environment variables
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "Error: OPENAI_API_KEY environment variable is not set." >&2
  echo "Please set it with: export OPENAI_API_KEY='your-api-key-here'" >&2
  exit 1
fi

echo "Setting up secure environment variables for deployment..."
echo "Using OPENAI_API_KEY from environment (${#OPENAI_API_KEY} characters)"

# Set the environment variable as a secret in Cloudflare Workers
echo "Setting OPENAI_API_KEY as a secret..."
echo "$OPENAI_API_KEY" | $WRANGLER_CMD secret put OPENAI_API_KEY --config "$SCRIPT_DIR/wrangler.jsonc"

echo "Deploying Cloudflare Worker using: $WRANGLER_CMD"
set +e
DEPLOY_OUTPUT=$($WRANGLER_CMD deploy --config "$SCRIPT_DIR/wrangler.jsonc" 2>&1)
STATUS=$?
set -e

echo "$DEPLOY_OUTPUT"

if [ $STATUS -ne 0 ]; then
  echo "Deployment failed." >&2
  exit $STATUS
fi

URL=$(printf "%s\n" "$DEPLOY_OUTPUT" | grep -Eo 'https?://[a-zA-Z0-9.-]+\.workers\.dev' | tail -n1 || true)
if [ -z "${URL:-}" ]; then
  echo "Could not detect the deployed URL from the output. Please review the logs above." >&2
  exit 1
fi

echo "Testing endpoint: $URL"
RESPONSE=$(curl -sS -H 'accept: application/json' "$URL") || true

echo "Response:"
echo "$RESPONSE"

if echo "$RESPONSE" | grep -q '"ok": *true'; then
  echo "Smoke test passed."
  echo "Worker deployed successfully with secure environment variables!"
else
  echo "Smoke test failed: expected to find '"ok": true' in the response." >&2
  exit 1
fi 