#!/usr/bin/env bash
set -euo pipefail
JOB_KEY="${JOB_KEY:-unknown}"
JOB_NAME="${JOB_NAME:-unknown}"
JOB_SELECTED_TOOL="${JOB_SELECTED_TOOL:-}"
DELIVERY_EXECUTION_MODE="${DELIVERY_EXECUTION_MODE:-default}"
DELIVERY_TARGET="${DELIVERY_TARGET:-bundle}"
OUT_JSON="runtime/executor_outputs/${JOB_KEY}.json"
STAMP=$(date +%Y%m%d%H%M%S)
BUNDLE_DIR="runtime/delivery_bundle/${JOB_KEY}_${STAMP}"
mkdir -p "$BUNDLE_DIR"

MANIFEST_JSON="${BUNDLE_DIR}/delivery_manifest.json"
README_MD="${BUNDLE_DIR}/README.md"
ARCHIVE_TGZ="${BUNDLE_DIR}.tar.gz"
EXTRA_FILE=""

python3 - <<'PY'
import json
from pathlib import Path
import os

job_key = os.environ.get("JOB_KEY", "unknown")
job_name = os.environ.get("JOB_NAME", "unknown")
selected_tool = os.environ.get("JOB_SELECTED_TOOL", "")
delivery_mode = os.environ.get("DELIVERY_EXECUTION_MODE", "default")
delivery_target = os.environ.get("DELIVERY_TARGET", "bundle")
bundle_root = Path("runtime/delivery_bundle")
target_dir = max([p for p in bundle_root.glob(f"{job_key}_*") if p.is_dir()], key=lambda p: p.stat().st_mtime)

executor_outputs = sorted(Path("runtime/executor_outputs").glob("job_*.json"))
generated_build = sorted(Path("runtime/generated_build").glob("**/*"))
testing_reports = sorted(Path("runtime/testing_reports").glob("**/*"))
codex_results = sorted(Path("runtime/codex_results").glob("**/*"))

payload = {
    "job_key": job_key,
    "executor": "delivery_agent",
    "job_name": job_name,
    "status": "completed",
    "selected_tool": selected_tool,
    "delivery_mode": delivery_mode,
    "delivery_target": delivery_target,
    "bundle_dir": str(target_dir),
    "collected": {
        "executor_outputs": [str(p) for p in executor_outputs if p.is_file()],
        "generated_build_files": [str(p) for p in generated_build if p.is_file()],
        "testing_report_files": [str(p) for p in testing_reports if p.is_file()],
        "codex_result_files": [str(p) for p in codex_results if p.is_file()],
    },
    "summary": "已汇总执行输出、构建产物、测试报告和 Codex 结果，生成交付清单"
}
(target_dir / "delivery_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
PY

case "${DELIVERY_EXECUTION_MODE}" in
  docker_compose)
    EXTRA_FILE="${BUNDLE_DIR}/docker-compose.generated.yml"
    cat > "$EXTRA_FILE" <<EOF
version: "3.9"
services:
  autofabric-backend:
    image: autofabric/backend:latest
    ports:
      - "8000:8000"
  autofabric-frontend:
    image: autofabric/frontend:latest
    ports:
      - "5173:5173"
EOF
    ;;
  github_actions)
    EXTRA_FILE="${BUNDLE_DIR}/github-actions.workflow.yml"
    cat > "$EXTRA_FILE" <<EOF
name: autofabric-preview
on:
  workflow_dispatch:
jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run E2E gate
        run: npm run gate:e2e
EOF
    ;;
  preview_runtime)
    EXTRA_FILE="${BUNDLE_DIR}/preview-runtime.json"
    cat > "$EXTRA_FILE" <<EOF
{
  "entry": "http://127.0.0.1:5173",
  "api": "http://127.0.0.1:8000",
  "mode": "preview_runtime",
  "job_key": "${JOB_KEY}"
}
EOF
    ;;
esac

cat > "$README_MD" <<EOF
# Delivery Bundle

## Job
- key: ${JOB_KEY}
- name: ${JOB_NAME}
- selected_tool: ${JOB_SELECTED_TOOL}
- delivery_mode: ${DELIVERY_EXECUTION_MODE}
- delivery_target: ${DELIVERY_TARGET}

## Bundle Content
本目录汇总：
- executor_outputs
- generated_build
- testing_reports
- codex_results

## Main Files
- ${MANIFEST_JSON}
- ${README_MD}
- ${EXTRA_FILE:-"(no extra adapter file)"}
- ${ARCHIVE_TGZ}
EOF

tar -czf "$ARCHIVE_TGZ" "$BUNDLE_DIR"

cat > "$OUT_JSON" <<EOF
{
  "job_key": "${JOB_KEY}",
  "executor": "delivery_agent",
  "job_name": "${JOB_NAME}",
  "status": "completed",
  "summary": "已生成版本化交付目录与打包文件",
  "selected_tool": "${JOB_SELECTED_TOOL}",
  "delivery_execution_mode": "${DELIVERY_EXECUTION_MODE}",
  "delivery_target": "${DELIVERY_TARGET}",
  "bundle_dir": "${BUNDLE_DIR}",
  "bundle_files": [
    "${MANIFEST_JSON}",
    "${README_MD}",
    "${EXTRA_FILE}",
    "${ARCHIVE_TGZ}"
  ]
}
EOF
echo "[delivery_agent] completed -> ${JOB_KEY}"
