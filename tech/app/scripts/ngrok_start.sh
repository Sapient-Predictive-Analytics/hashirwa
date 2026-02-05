#!/usr/bin/env bash
set -euo pipefail
# Expose the Flask UI+API app (default port 8080)
ngrok http 8080
