from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import os
import subprocess


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def run_openclaw_task(
    *,
    task_name: str,
    payload: dict[str, Any],
    outcome_id: int,
) -> dict[str, Any]:
    bridge_cmd = os.getenv("OPENCLAW_BRIDGE_CMD")
    artifact_dir = Path(f".autofabric_runs/outcome_{outcome_id}/openclaw")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    request = {
        "task_name": task_name,
        "payload": payload,
        "outcome_id": outcome_id,
        "executed_at": _utc_now(),
    }

    request_path = artifact_dir / "openclaw_request.json"
    request_path.write_text(
        json.dumps(request, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if not bridge_cmd:
        response = {
            "executor": "openclaw",
            "task_name": task_name,
            "status": "accepted",
            "mode": "placeholder",
            "message": "OpenClaw executor placeholder accepted the task.",
            "received_payload": payload,
            "executed_at": _utc_now(),
        }
    else:
        try:
            completed = subprocess.run(
                [bridge_cmd, str(request_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            stdout_text = (completed.stdout or "").strip()
            stderr_text = (completed.stderr or "").strip()

            parsed_stdout: Any
            try:
                parsed_stdout = json.loads(stdout_text) if stdout_text else {}
            except Exception:
                parsed_stdout = {"raw_stdout": stdout_text}

            response = {
                "executor": "openclaw",
                "task_name": task_name,
                "status": "completed" if completed.returncode == 0 else "failed",
                "mode": "bridge",
                "returncode": completed.returncode,
                "stdout": parsed_stdout,
                "stderr": stderr_text,
                "executed_at": _utc_now(),
            }
        except Exception as e:
            response = {
                "executor": "openclaw",
                "task_name": task_name,
                "status": "error",
                "mode": "bridge",
                "error": str(e),
                "executed_at": _utc_now(),
            }

    response_path = artifact_dir / "openclaw_response.json"
    response_path.write_text(
        json.dumps(response, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    artifact_ref = f"openclaw-trace-{outcome_id}"

    return {
        "executor_name": "openclaw",
        "task_name": task_name,
        "status": response["status"],
        "input_payload": request,
        "output_payload": response,
        "artifact": {
            "artifact_type": "openclaw_trace",
            "file_path": str(artifact_dir),
            "artifact_ref": artifact_ref,
            "artifact_metadata": {
                "request_path": str(request_path),
                "response_path": str(response_path),
                "mode": response.get("mode"),
                "task_name": task_name,
            },
        },
        "current_result": {
            "stage": "browser_execution_completed"
            if response["status"] in {"accepted", "completed"}
            else "browser_execution_failed",
            "summary": response.get("message")
            or f"OpenClaw task {task_name} finished with status={response['status']}.",
            "artifact": {
                "type": "openclaw_trace",
                "ref": artifact_ref,
                "workspace_dir": str(artifact_dir),
            },
            "openclaw": response,
        },
    }
