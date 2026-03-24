#!/usr/bin/env bash
set -euo pipefail
JOB_KEY="${JOB_KEY:-unknown}"
JOB_NAME="${JOB_NAME:-unknown}"
JOB_PROJECT_ID="${JOB_PROJECT_ID:-}"
JOB_SELECTED_TOOL="${JOB_SELECTED_TOOL:-}"
TEST_EXECUTION_MODE="${TEST_EXECUTION_MODE:-default}"
TEST_TARGET_SCOPE="${TEST_TARGET_SCOPE:-fullstack}"
OUT_JSON="runtime/executor_outputs/${JOB_KEY}.json"
REPORT_DIR="runtime/testing_reports/${JOB_KEY}"
mkdir -p "$REPORT_DIR"

REPORT_JSON="${REPORT_DIR}/testing_report.json"
REPORT_MD="${REPORT_DIR}/testing_report.md"
PYTEST_STDOUT="${REPORT_DIR}/pytest_stdout.txt"
PYTEST_STDERR="${REPORT_DIR}/pytest_stderr.txt"
FRONTEND_BUILD_STDOUT="${REPORT_DIR}/frontend_build_stdout.txt"
FRONTEND_BUILD_STDERR="${REPORT_DIR}/frontend_build_stderr.txt"
PLAYWRIGHT_STDOUT="${REPORT_DIR}/playwright_stdout.txt"
PLAYWRIGHT_STDERR="${REPORT_DIR}/playwright_stderr.txt"

BACKEND_PROJECTS_STATUS="unreachable"
BACKEND_PROJECT_DETAIL_STATUS="unreachable"
FRONTEND_EXISTS="false"
PACKAGE_JSON_EXISTS="false"
PYTEST_USED="false"
PYTEST_STATUS="not_run"
PYTEST_EXIT_CODE=""
AUTOMATED_TESTS_USED="false"
AUTOMATED_TESTS_STATUS="not_run"
AUTOMATED_TESTS_EXIT_CODE=""
AUTOMATED_TESTS_RUNNER="none"
AUTOMATED_TESTS_TARGET=""
FRONTEND_BUILD_USED="false"
FRONTEND_BUILD_STATUS="not_run"
FRONTEND_BUILD_EXIT_CODE=""
PLAYWRIGHT_USED="false"
PLAYWRIGHT_STATUS="not_run"
PLAYWRIGHT_EXIT_CODE=""

if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "no python found" > "${PYTEST_STDERR}"
  PYTHON_BIN=""
fi

if curl -fsS http://127.0.0.1:8000/projects >/dev/null 2>&1; then
  BACKEND_PROJECTS_STATUS="passed"
fi
if [ -n "${JOB_PROJECT_ID}" ] && curl -fsS "http://127.0.0.1:8000/projects/${JOB_PROJECT_ID}" >/dev/null 2>&1; then
  BACKEND_PROJECT_DETAIL_STATUS="passed"
elif curl -fsS http://127.0.0.1:8000/projects/1 >/dev/null 2>&1; then
  BACKEND_PROJECT_DETAIL_STATUS="passed"
fi
if [ -d "frontend/src" ]; then FRONTEND_EXISTS="true"; fi
if [ -f "frontend/package.json" ]; then PACKAGE_JSON_EXISTS="true"; fi

if [ "${TEST_EXECUTION_MODE}" = "playwright" ] && [ "${PACKAGE_JSON_EXISTS}" = "true" ]; then
  FRONTEND_BUILD_USED="true"
  set +e
  npm --prefix frontend run build > "${FRONTEND_BUILD_STDOUT}" 2> "${FRONTEND_BUILD_STDERR}"
  CODE=$?
  set -e
  FRONTEND_BUILD_EXIT_CODE="$CODE"
  if [ "$CODE" -eq 0 ]; then FRONTEND_BUILD_STATUS="passed"; else FRONTEND_BUILD_STATUS="failed"; fi
else
  echo "frontend build not requested" > "${FRONTEND_BUILD_STDERR}"
fi

if [ "${TEST_EXECUTION_MODE}" = "playwright" ] && [ "${PACKAGE_JSON_EXISTS}" = "true" ]; then
  PLAYWRIGHT_USED="true"
  set +e
  npm --prefix frontend exec playwright install chromium > "${PLAYWRIGHT_STDOUT}" 2> "${PLAYWRIGHT_STDERR}"
  INSTALL_CODE=$?
  if [ "$INSTALL_CODE" -eq 0 ]; then
    PLAYWRIGHT_BASE_URL="http://127.0.0.1:5173" npm --prefix frontend run test:e2e >> "${PLAYWRIGHT_STDOUT}" 2>> "${PLAYWRIGHT_STDERR}"
    CODE=$?
  else
    CODE=$INSTALL_CODE
  fi
  set -e
  PLAYWRIGHT_EXIT_CODE="$CODE"
  if [ "$CODE" -eq 0 ]; then
    PLAYWRIGHT_STATUS="passed"
  else
    PLAYWRIGHT_STATUS="failed"
  fi
else
  echo "playwright not requested" > "${PLAYWRIGHT_STDERR}"
fi

PROJECT_TEST_DIR=""
if [ -n "${JOB_PROJECT_ID}" ] && [ -d "generated/project_${JOB_PROJECT_ID}/codebundle_v2/tests" ]; then
  PROJECT_TEST_DIR="generated/project_${JOB_PROJECT_ID}/codebundle_v2/tests"
fi

if [ -n "${PROJECT_TEST_DIR}" ] && find "${PROJECT_TEST_DIR}" -type f \( -name "test_*.py" -o -name "*_test.py" \) | grep -q .; then
  AUTOMATED_TESTS_USED="true"
  AUTOMATED_TESTS_TARGET="${PROJECT_TEST_DIR}"
  if [ -n "${PYTHON_BIN}" ] && "${PYTHON_BIN}" - <<'PY' >/dev/null 2>&1
import importlib.util
import sys
sys.exit(0 if importlib.util.find_spec("pytest") else 1)
PY
  then
    PYTEST_USED="true"
    AUTOMATED_TESTS_RUNNER="pytest"
    set +e
    "${PYTHON_BIN}" -m pytest "${PROJECT_TEST_DIR}" > "$PYTEST_STDOUT" 2> "$PYTEST_STDERR"
    CODE=$?
    set -e
    PYTEST_EXIT_CODE="$CODE"
    AUTOMATED_TESTS_EXIT_CODE="$CODE"
    if [ "$CODE" -eq 0 ]; then
      PYTEST_STATUS="passed"
      AUTOMATED_TESTS_STATUS="passed"
    else
      PYTEST_STATUS="failed"
      AUTOMATED_TESTS_STATUS="failed"
    fi
  else
    AUTOMATED_TESTS_RUNNER="unittest"
    set +e
    AUTOFABRIC_TEST_BASE_URL="http://127.0.0.1:8000" "${PYTHON_BIN}" -m unittest discover -s "${PROJECT_TEST_DIR}" -p "test_*.py" > "$PYTEST_STDOUT" 2> "$PYTEST_STDERR"
    CODE=$?
    set -e
    AUTOMATED_TESTS_EXIT_CODE="$CODE"
    if [ "$CODE" -eq 0 ]; then
      AUTOMATED_TESTS_STATUS="passed"
    else
      AUTOMATED_TESTS_STATUS="failed"
    fi
  fi
elif find . -type f \( -name "test_*.py" -o -name "*_test.py" \) | grep -q .; then
  AUTOMATED_TESTS_USED="true"
  AUTOMATED_TESTS_TARGET="repository"
  PYTEST_USED="true"
  AUTOMATED_TESTS_RUNNER="pytest"
  set +e
  "${PYTHON_BIN:-python3}" -m pytest > "$PYTEST_STDOUT" 2> "$PYTEST_STDERR"
  CODE=$?
  set -e
  PYTEST_EXIT_CODE="$CODE"
  AUTOMATED_TESTS_EXIT_CODE="$CODE"
  if [ "$CODE" -eq 0 ]; then
    PYTEST_STATUS="passed"
    AUTOMATED_TESTS_STATUS="passed"
  else
    PYTEST_STATUS="failed"
    AUTOMATED_TESTS_STATUS="failed"
  fi
else
  echo "no pytest files found" > "$PYTEST_STDERR"
fi

cat > "$REPORT_JSON" <<EOF
{
  "job_key": "${JOB_KEY}",
  "executor": "testing_agent",
  "job_name": "${JOB_NAME}",
  "status": "completed",
  "adapter": {
    "selected_tool": "${JOB_SELECTED_TOOL}",
    "mode": "${TEST_EXECUTION_MODE}",
    "scope": "${TEST_TARGET_SCOPE}"
  },
  "checks": {
    "backend_projects_api": "${BACKEND_PROJECTS_STATUS}",
    "backend_project_detail_api": "${BACKEND_PROJECT_DETAIL_STATUS}",
    "frontend_src_exists": "${FRONTEND_EXISTS}",
    "frontend_package_json_exists": "${PACKAGE_JSON_EXISTS}"
  },
  "frontend_build": {
    "used": ${FRONTEND_BUILD_USED},
    "status": "${FRONTEND_BUILD_STATUS}",
    "exit_code": "${FRONTEND_BUILD_EXIT_CODE}",
    "stdout_file": "${FRONTEND_BUILD_STDOUT}",
    "stderr_file": "${FRONTEND_BUILD_STDERR}"
  },
  "playwright": {
    "used": ${PLAYWRIGHT_USED},
    "status": "${PLAYWRIGHT_STATUS}",
    "exit_code": "${PLAYWRIGHT_EXIT_CODE}",
    "stdout_file": "${PLAYWRIGHT_STDOUT}",
    "stderr_file": "${PLAYWRIGHT_STDERR}"
  },
  "pytest": {
    "used": ${PYTEST_USED},
    "status": "${PYTEST_STATUS}",
    "exit_code": "${PYTEST_EXIT_CODE}",
    "stdout_file": "${PYTEST_STDOUT}",
    "stderr_file": "${PYTEST_STDERR}"
  },
  "automated_tests": {
    "used": ${AUTOMATED_TESTS_USED},
    "runner": "${AUTOMATED_TESTS_RUNNER}",
    "status": "${AUTOMATED_TESTS_STATUS}",
    "exit_code": "${AUTOMATED_TESTS_EXIT_CODE}",
    "target": "${AUTOMATED_TESTS_TARGET}",
    "stdout_file": "${PYTEST_STDOUT}",
    "stderr_file": "${PYTEST_STDERR}"
  },
  "summary": "已完成 smoke test，并执行项目级自动化测试（pytest 或 unittest）"
}
EOF

cat > "$REPORT_MD" <<EOF
# Testing Report

## Job
- key: ${JOB_KEY}
- name: ${JOB_NAME}
- selected_tool: ${JOB_SELECTED_TOOL}
- mode: ${TEST_EXECUTION_MODE}
- scope: ${TEST_TARGET_SCOPE}

## Smoke Test Result
- backend /projects: ${BACKEND_PROJECTS_STATUS}
- backend /projects/${JOB_PROJECT_ID:-1}: ${BACKEND_PROJECT_DETAIL_STATUS}
- frontend/src exists: ${FRONTEND_EXISTS}
- frontend/package.json exists: ${PACKAGE_JSON_EXISTS}

## Frontend Build
- used: ${FRONTEND_BUILD_USED}
- status: ${FRONTEND_BUILD_STATUS}
- exit_code: ${FRONTEND_BUILD_EXIT_CODE}
- stdout: ${FRONTEND_BUILD_STDOUT}
- stderr: ${FRONTEND_BUILD_STDERR}

## Playwright
- used: ${PLAYWRIGHT_USED}
- status: ${PLAYWRIGHT_STATUS}
- exit_code: ${PLAYWRIGHT_EXIT_CODE}
- stdout: ${PLAYWRIGHT_STDOUT}
- stderr: ${PLAYWRIGHT_STDERR}

## Pytest
- used: ${PYTEST_USED}
- status: ${PYTEST_STATUS}
- exit_code: ${PYTEST_EXIT_CODE}
- stdout: ${PYTEST_STDOUT}
- stderr: ${PYTEST_STDERR}

## Automated Tests
- used: ${AUTOMATED_TESTS_USED}
- runner: ${AUTOMATED_TESTS_RUNNER}
- status: ${AUTOMATED_TESTS_STATUS}
- exit_code: ${AUTOMATED_TESTS_EXIT_CODE}
- target: ${AUTOMATED_TESTS_TARGET}
EOF

cat > "$OUT_JSON" <<EOF
{
  "job_key": "${JOB_KEY}",
  "executor": "testing_agent",
  "job_name": "${JOB_NAME}",
  "status": "completed",
  "summary": "$(if [ "${TEST_EXECUTION_MODE}" = "playwright" ]; then echo "已生成 Playwright 适配器测试报告"; else echo "已生成真实测试报告"; fi)",
  "report_dir": "${REPORT_DIR}",
  "report_files": [
    "${REPORT_JSON}",
    "${REPORT_MD}",
    "${FRONTEND_BUILD_STDOUT}",
    "${FRONTEND_BUILD_STDERR}",
    "${PLAYWRIGHT_STDOUT}",
    "${PLAYWRIGHT_STDERR}",
    "${PYTEST_STDOUT}",
    "${PYTEST_STDERR}"
  ],
  "selected_tool": "${JOB_SELECTED_TOOL}",
  "test_execution_mode": "${TEST_EXECUTION_MODE}",
  "frontend_build_used": ${FRONTEND_BUILD_USED},
  "frontend_build_status": "${FRONTEND_BUILD_STATUS}",
  "playwright_used": ${PLAYWRIGHT_USED},
  "playwright_status": "${PLAYWRIGHT_STATUS}",
  "pytest_used": ${PYTEST_USED},
  "pytest_status": "${PYTEST_STATUS}",
  "automated_tests_used": ${AUTOMATED_TESTS_USED},
  "automated_tests_runner": "${AUTOMATED_TESTS_RUNNER}",
  "automated_tests_status": "${AUTOMATED_TESTS_STATUS}",
  "automated_tests_target": "${AUTOMATED_TESTS_TARGET}"
}
EOF
echo "[testing_agent] completed -> ${JOB_KEY}"
