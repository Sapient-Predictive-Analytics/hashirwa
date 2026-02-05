#!/usr/bin/env bash
set -euo pipefail

# List of issuer IDs to refresh
ISSUERS=(1 2 3)

# Local HashiRWA endpoint
BASE="http://127.0.0.1:8080"

for id in "${ISSUERS[@]}"; do
  echo "[scheduled] triggering Chainlink price refresh for issuer_id=$id"
  curl -s -X POST "${BASE}/api/v1/admin/trigger_chainlink_price?issuer_id=${id}" >/dev/null
done

echo "[scheduled] done"
