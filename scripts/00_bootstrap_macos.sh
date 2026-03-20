#!/usr/bin/env bash
set -euo pipefail

echo "[1/7] 检查 Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  echo "请先安装 Homebrew: https://brew.sh"
  exit 1
fi

echo "[2/7] 安装基础工具"
brew install python@3.12 node git jq tree docker colima

echo "[3/7] 启动 Colima"
colima start --cpu 4 --memory 8 || true

echo "[4/7] 创建 Python 虚拟环境"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[5/7] 准备环境变量"
[ -f .env ] || cp .env.example .env

echo "[6/7] 启动 PostgreSQL 容器"
docker compose up -d postgres

echo "[7/7] 等待数据库就绪"
sleep 8

echo "完成。下一步执行: bash scripts/01_init_project.sh"
