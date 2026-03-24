"""OpenClaw Bridge — unified dispatch layer for execution jobs.

Supports three modes (configured via OPENCLAW_BRIDGE_MODE):
- "llm"   — in-process LLM code generation (default, no shell dependency)
- "shell" — subprocess to scripts/openclaw_bridge_runner.py
- "mock"  — instant success, for testing/demo
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from app.config import config
from app.stages.execution import execute_plan


def dispatch(project_id: int, jobs: list[dict]) -> dict:
    """Dispatch jobs to the configured OpenClaw bridge mode."""
    mode = config.openclaw.bridge_mode

    if mode == "llm":
        return _dispatch_llm(project_id, jobs)
    elif mode == "shell":
        return _dispatch_shell(project_id, jobs)
    else:
        return _dispatch_mock(project_id, jobs)


def _dispatch_llm(project_id: int, jobs: list[dict]) -> dict:
    """Execute jobs in-process using LLM code generation."""
    return execute_plan(project_id, jobs)


def _dispatch_shell(project_id: int, jobs: list[dict]) -> dict:
    """Execute via openclaw_bridge_runner.py subprocess."""
    root = Path(__file__).resolve().parents[2]
    runner = root / "scripts" / "openclaw_bridge_runner.py"

    if not runner.exists():
        return {
            "project_id": project_id,
            "status": "error",
            "error": f"Bridge runner not found: {runner}",
        }

    # Build request payload file
    request_payload = {
        "project_id": project_id,
        "dispatch_id": f"project_{project_id}",
        "openclaw_payload": {
            "jobs": jobs,
        },
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, prefix="openclaw_req_"
    ) as f:
        json.dump(request_payload, f, ensure_ascii=False, indent=2)
        request_path = f.name

    result_path = tempfile.mktemp(suffix=".json", prefix="openclaw_res_")

    try:
        completed = subprocess.run(
            ["python3", str(runner)],
            cwd=str(root),
            env={
                **__import__("os").environ,
                "OPENCLAW_BRIDGE_REQUEST_PATH": request_path,
                "OPENCLAW_BRIDGE_RESULT_PATH": result_path,
            },
            capture_output=True,
            text=True,
            timeout=config.openclaw.executor_timeout,
        )

        # Try to read result file
        result_file = Path(result_path)
        if result_file.exists():
            bridge_result = json.loads(result_file.read_text())
        else:
            bridge_result = {}

        return {
            "project_id": project_id,
            "status": "completed" if completed.returncode == 0 else "failed",
            "exit_code": completed.returncode,
            "stdout": completed.stdout[-3000:],
            "stderr": completed.stderr[-1000:],
            "bridge_result": bridge_result,
        }
    except subprocess.TimeoutExpired:
        return {
            "project_id": project_id,
            "status": "timeout",
            "error": f"Bridge timed out after {config.openclaw.executor_timeout}s",
        }
    except Exception as e:
        return {
            "project_id": project_id,
            "status": "error",
            "error": str(e),
        }


def _dispatch_mock(project_id: int, jobs: list[dict]) -> dict:
    """Return instant success for testing/demo."""
    return {
        "project_id": project_id,
        "total_jobs": len(jobs),
        "completed": len(jobs),
        "job_results": [
            {
                "job_id": job.get("job_id", f"mock_{i}"),
                "status": "completed",
                "files_written": [],
                "summary": f"[mock] Job completed: {job.get('payload', {}).get('task_name', 'unknown')}",
                "dependencies": [],
            }
            for i, job in enumerate(jobs)
        ],
    }
