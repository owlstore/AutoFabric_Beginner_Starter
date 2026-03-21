from typing import Any
from datetime import datetime
import subprocess
import json
import os

def run_openclaw_task(task_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Day 21:
    先做安全的本地桥接版本。
    默认通过环境变量 OPENCLAW_BRIDGE_CMD 指定桥接命令。
    如果没配置，就走 placeholder。
    """

    bridge_cmd = os.getenv("OPENCLAW_BRIDGE_CMD")

    if not bridge_cmd:
        return {
            "executor": "openclaw",
            "task_name": task_name,
            "status": "accepted",
            "mode": "placeholder",
            "received_payload": payload,
            "message": "OpenClaw executor placeholder accepted the task.",
            "executed_at": datetime.utcnow().isoformat() + "Z"
        }

    request = {
        "task_name": task_name,
        "payload": payload,
    }

    try:
        completed = subprocess.run(
            [bridge_cmd, json.dumps(request, ensure_ascii=False)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "executor": "openclaw",
            "task_name": task_name,
            "status": "completed" if completed.returncode == 0 else "failed",
            "mode": "bridge",
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "executed_at": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        return {
            "executor": "openclaw",
            "task_name": task_name,
            "status": "error",
            "mode": "bridge",
            "error": str(e),
            "executed_at": datetime.utcnow().isoformat() + "Z"
        }
