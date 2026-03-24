#!/usr/bin/env bash
set -euo pipefail
JOB_KEY="${JOB_KEY:-unknown}"
JOB_NAME="${JOB_NAME:-unknown}"
JOB_SELECTED_TOOL="${JOB_SELECTED_TOOL:-}"
TOOL_ADAPTER_MODE="${TOOL_ADAPTER_MODE:-default}"
OUT="runtime/executor_outputs/${JOB_KEY}.json"
OUT_DIR="docs/autofabric"
mkdir -p "$OUT_DIR"
SAFE_NAME=$(python3 - <<'PY'
import os, re
name = os.environ.get("JOB_NAME", "planner")
name = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", name)
print(name[:80])
PY
)
FILE="${OUT_DIR}/autofabric_${SAFE_NAME}.md"
cat > "$FILE" <<EOF
# ${JOB_NAME}

- executor: planner_agent
- job_key: ${JOB_KEY}
- selected_tool: ${JOB_SELECTED_TOOL}
- tool_adapter_mode: ${TOOL_ADAPTER_MODE}

这是 planner_agent 自动生成的规划文档骨架。
EOF
cat > "$OUT" <<EOF
{
  "job_key": "$JOB_KEY",
  "executor": "planner_agent",
  "job_name": "$JOB_NAME",
  "status": "completed",
  "summary": "已生成编排/数据库/API 规划骨架",
  "selected_tool": "${JOB_SELECTED_TOOL}",
  "tool_adapter_mode": "${TOOL_ADAPTER_MODE}",
  "generated_file": "$FILE"
}
EOF
echo "[planner_agent] completed -> $JOB_KEY"
