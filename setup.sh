#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure npm (Node.js) exists, attempt to install via Homebrew if missing
if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Attempting to install Node.js via Homebrew..."
  if command -v brew >/dev/null 2>&1; then
    brew install node
  else
    echo "Homebrew is not installed. Please install Node.js from https://nodejs.org and re-run this script." >&2
    exit 1
  fi
fi

# Install or update Wrangler globally
if ! command -v wrangler >/dev/null 2>&1; then
  echo "Installing Wrangler globally via npm..."
  npm install -g wrangler
else
  echo "Wrangler already installed: $(wrangler --version)"
  echo "Updating Wrangler to the latest version..."
  npm install -g wrangler
fi

echo "Wrangler version: $(wrangler --version)"

# Authenticate with Cloudflare if not already authenticated
if wrangler whoami >/dev/null 2>&1; then
  echo "You are already authenticated with Cloudflare."
else
  echo "You are not logged in to Cloudflare. Launching browser for 'wrangler login'..."
  wrangler login
fi

echo "Setup complete. You can now run ./deploy.sh or ./run_local.sh" 