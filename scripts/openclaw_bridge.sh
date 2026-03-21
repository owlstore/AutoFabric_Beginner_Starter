#!/bin/bash
set -euo pipefail

REQUEST_PATH="${1:?missing request json path}"

python3 - <<'PY' "$REQUEST_PATH"
import json
import sys
from pathlib import Path

request_path = Path(sys.argv[1])
data = json.loads(request_path.read_text(encoding="utf-8"))

task_name = data.get("task_name")
payload = data.get("payload", {})

mapped = {
    "inspect_order_submission_ui": {
        "bridge_status": "ok",
        "handler": "inspect_order_submission_ui",
        "message": "Simulated inspection of order submission failure UI.",
    },
    "locate_payment_module": {
        "bridge_status": "ok",
        "handler": "locate_payment_module",
        "message": "Simulated module location for payment failure.",
    },
    "collect_system_analysis_context": {
        "bridge_status": "ok",
        "handler": "collect_system_analysis_context",
        "message": "Simulated collection of system analysis context.",
    },
}

result = mapped.get(task_name, {
    "bridge_status": "ok",
    "handler": task_name,
    "message": "Fallback OpenClaw bridge handler executed.",
})

result["received_payload"] = payload
print(json.dumps(result, ensure_ascii=False))
PY
