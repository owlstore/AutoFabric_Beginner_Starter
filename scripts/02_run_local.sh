#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
