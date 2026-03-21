#!/usr/bin/env bash
set -e

BASE_URL="http://127.0.0.1:8000"

RESP=$(curl -s -X POST "$BASE_URL/entry/submit" \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Analyze this order dashboard service"}')

echo "=== ENTRY RESP ==="
echo "$RESP" | jq
echo

OUTCOME_ID=$(echo "$RESP" | jq -r '.outcome_id')
GOAL_ID=$(echo "$RESP" | jq -r '.goal_id')

if [ -z "$OUTCOME_ID" ] || [ "$OUTCOME_ID" = "null" ]; then
  echo "ERROR: outcome_id missing"
  exit 1
fi

if [ -z "$GOAL_ID" ] || [ "$GOAL_ID" = "null" ]; then
  echo "ERROR: goal_id missing"
  exit 1
fi

echo "=== EXECUTE ==="
curl -s -X POST "$BASE_URL/outcomes/$OUTCOME_ID/execute" | jq
echo

echo "=== TIMELINE ==="
curl -s "$BASE_URL/outcomes/$OUTCOME_ID/timeline" | jq
echo

echo "=== WORKSPACE DETAIL ==="
curl -s "$BASE_URL/workspaces/detail/$GOAL_ID" | jq '.summary'
echo

echo "=== WORKSPACES COMPLETED COUNT ==="
curl -s "$BASE_URL/workspaces?status=completed" | jq '.count'
echo

echo "smoke test passed"
