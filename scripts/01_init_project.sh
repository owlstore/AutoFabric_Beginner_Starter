#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate

echo "导入初始表结构"
docker exec -i autofabric-postgres psql -U autofabric -d autofabric < sql/001_init.sql

echo "项目目录确认"
tree -L 2 app sql scripts || true

echo "完成。下一步执行: bash scripts/02_run_local.sh"
