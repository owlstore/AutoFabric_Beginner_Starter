#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:8000"
INPUT='{"user_input":"Analyze this order dashboard service"}'

echo "=== HEALTH ==="
curl -s "$BASE_URL/health" | jq
echo

echo "=== ENTRY ==="
RESP=$(curl -s -X POST "$BASE_URL/entry/submit" \
  -H "Content-Type: application/json" \
  -d "$INPUT")

echo "$RESP" | jq
echo

OUTCOME_ID=$(echo "$RESP" | jq -r '.outcome_id')

if [ -z "$OUTCOME_ID" ] || [ "$OUTCOME_ID" = "null" ]; then
  echo "ERROR: outcome_id empty"
  exit 1
fi

echo "OUTCOME_ID=$OUTCOME_ID"
echo

echo "=== EXECUTE FIRST ==="
curl -s -X POST "$BASE_URL/outcomes/$OUTCOME_ID/execute" | jq
echo

echo "=== EXECUTE SECOND (IDEMPOTENT) ==="
curl -s -X POST "$BASE_URL/outcomes/$OUTCOME_ID/execute" | jq
echo

echo "=== TIMELINE ==="
curl -s "$BASE_URL/outcomes/$OUTCOME_ID/timeline" | jq
echo

echo "=== WORKSPACES TOP 3 ==="
curl -s "$BASE_URL/workspaces" | jq '.items[:3]'
echo
