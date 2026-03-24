#!/usr/bin/env bash
set -euo pipefail

REQ_PATH="${OPENCLAW_BRIDGE_REQUEST_PATH:-}"
BRIDGE_ID="${OPENCLAW_BRIDGE_ID:-}"

if [ -z "$REQ_PATH" ]; then
  echo "OPENCLAW_BRIDGE_REQUEST_PATH is empty" >&2
  exit 1
fi
if [ ! -f "$REQ_PATH" ]; then
  echo "request file not found: $REQ_PATH" >&2
  exit 1
fi

exec python3 scripts/openclaw_bridge_runner.py
