#!/usr/bin/env bash
set -euo pipefail
JOB_KEY="${JOB_KEY:-unknown}"
JOB_NAME="${JOB_NAME:-unknown}"
JOB_SELECTED_TOOL="${JOB_SELECTED_TOOL:-}"
TOOL_ADAPTER_MODE="${TOOL_ADAPTER_MODE:-default}"
OUT="runtime/executor_outputs/${JOB_KEY}.json"
cat > "$OUT" <<EOF
{
  "job_key": "$JOB_KEY",
  "executor": "requirement_agent",
  "job_name": "$JOB_NAME",
  "status": "completed",
  "summary": "已生成需求卡骨架",
  "selected_tool": "${JOB_SELECTED_TOOL}",
  "tool_adapter_mode": "${TOOL_ADAPTER_MODE}"
}
EOF
echo "[requirement_agent] completed -> $JOB_KEY"
