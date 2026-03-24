#!/usr/bin/env bash
set -euo pipefail

JOB_KEY="${JOB_KEY:-unknown}"
JOB_NAME="${JOB_NAME:-unknown}"
JOB_PROJECT_ID="${JOB_PROJECT_ID:-}"
JOB_SELECTED_TOOL="${JOB_SELECTED_TOOL:-}"
BROWSER_EXECUTION_MODE="${BROWSER_EXECUTION_MODE:-default}"

OUT_JSON="runtime/executor_outputs/${JOB_KEY}.json"
ACTION_DIR="runtime/browser_actions/${JOB_KEY}"
ACTION_JSON="${ACTION_DIR}/browser_action.json"

mkdir -p "$ACTION_DIR"

cat > "$ACTION_JSON" <<EOF
{
  "job_key": "${JOB_KEY}",
  "job_name": "${JOB_NAME}",
  "project_id": "${JOB_PROJECT_ID}",
  "selected_tool": "${JOB_SELECTED_TOOL}",
  "browser_execution_mode": "${BROWSER_EXECUTION_MODE}",
  "actions": [
    "open_workbench",
    "inspect_runtime_panel",
    "record_delivery_status"
  ],
  "status": "completed"
}
EOF

cat > "$OUT_JSON" <<EOF
{
  "job_key": "${JOB_KEY}",
  "executor": "openclaw_browser_agent",
  "job_name": "${JOB_NAME}",
  "status": "completed",
  "summary": "已生成浏览器执行动作记录",
  "selected_tool": "${JOB_SELECTED_TOOL}",
  "browser_execution_mode": "${BROWSER_EXECUTION_MODE}",
  "artifact_files": [
    "${ACTION_JSON}"
  ]
}
EOF

echo "[openclaw_browser_agent] completed -> ${JOB_KEY}"
