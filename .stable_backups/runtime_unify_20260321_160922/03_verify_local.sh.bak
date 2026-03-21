#!/usr/bin/env bash
set -euo pipefail

echo "[A] 健康检查"
curl -s http://127.0.0.1:8000/health | jq

echo "[B] 目标解析检查"
curl -s -X POST http://127.0.0.1:8000/goals/parse \
  -H 'Content-Type: application/json' \
  -d '{"raw_input":"帮我构建一个 Ubuntu 22.04 开发环境，带 Docker、Git、Python"}' | jq

echo "[C] OpenClaw 测试检查"
curl -s -X POST http://127.0.0.1:8000/openclaw/test | jq
