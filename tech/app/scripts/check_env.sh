#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for k in SEPOLIA_RPC_URL PRIVATE_KEY CONSUMER_ADDRESS SUBSCRIPTION_ID; do
  if ! grep -q "^${k}=" .env 2>/dev/null; then
    echo "Missing ${k} in .env"
    exit 1
  fi
done
echo "env OK"
