"""OpenClaw Bridge — unified dispatch layer for execution jobs.

Supports four modes (configured via OPENCLAW_BRIDGE_MODE):
- "llm"     — in-process LLM code generation (default, no shell dependency)
- "gateway" — dispatch to OpenClaw Gateway agent via CLI
- "shell"   — subprocess to scripts/openclaw_bridge_runner.py
- "mock"    — instant success, for testing/demo
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.config import config
from app.stages.execution import execute_plan

log = logging.getLogger(__name__)


def dispatch(project_id: int, jobs: list[dict]) -> dict:
    """Dispatch jobs to the configured OpenClaw bridge mode."""
    mode = config.openclaw.bridge_mode

    if mode == "llm":
        return _dispatch_llm(project_id, jobs)
    elif mode == "gateway":
        return _dispatch_gateway(project_id, jobs)
    elif mode == "shell":
        return _dispatch_shell(project_id, jobs)
    else:
        return _dispatch_mock(project_id, jobs)


def _dispatch_llm(project_id: int, jobs: list[dict]) -> dict:
    """Execute jobs in-process using LLM code generation."""
    return execute_plan(project_id, jobs)


def _dispatch_gateway(project_id: int, jobs: list[dict]) -> dict:
    """Execute jobs via OpenClaw Gateway agent CLI."""
    openclaw_bin = shutil.which("openclaw")
    if not openclaw_bin:
        log.warning("openclaw CLI not found, falling back to llm mode")
        return _dispatch_llm(project_id, jobs)

    results = []
    all_files_written: list[str] = []
    output_dir = Path(config.openclaw.output_dir) / f"project_{project_id}" / "src"
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, job in enumerate(jobs):
        job_id = job.get("job_id", f"gateway_{i}")
        task_desc = json.dumps(job, ensure_ascii=False)

        prompt = (
            f"Generate production-ready code for this task. "
            f"Output ONLY valid JSON with this structure: "
            f'{{"files": [{{"path": "relative/path.py", "content": "full code"}}], '
            f'"summary": "brief description"}}.\n\n'
            f"Task:\n{task_desc}"
        )

        try:
            completed = subprocess.run(
                [
                    openclaw_bin, "agent",
                    "--agent", config.openclaw.gateway_agent,
                    "--message", prompt,
                    "--json",
                    "--timeout", str(config.openclaw.executor_timeout),
                ],
                capture_output=True,
                text=True,
                timeout=config.openclaw.executor_timeout + 30,
            )

            if completed.returncode != 0:
                results.append({
                    "job_id": job_id,
                    "status": "failed",
                    "error": completed.stderr[-500:] if completed.stderr else "non-zero exit",
                    "files_written": [],
                })
                continue

            # Parse agent response — extract JSON from output
            agent_output = completed.stdout.strip()
            file_data = _extract_files_from_agent_output(agent_output)

            written = []
            for f in file_data:
                rel_path = f["path"]
                full_path = output_dir / rel_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(f["content"], encoding="utf-8")
                written.append(str(full_path))
                all_files_written.append(str(full_path))

            results.append({
                "job_id": job_id,
                "status": "completed",
                "files_written": written,
                "summary": f"Gateway agent generated {len(written)} files",
            })

        except subprocess.TimeoutExpired:
            results.append({
                "job_id": job_id,
                "status": "timeout",
                "error": f"Gateway agent timed out after {config.openclaw.executor_timeout}s",
                "files_written": [],
            })
        except Exception as e:
            log.exception("Gateway dispatch error for job %s", job_id)
            results.append({
                "job_id": job_id,
                "status": "error",
                "error": str(e),
                "files_written": [],
            })

    return {
        "project_id": project_id,
        "total_jobs": len(jobs),
        "completed": sum(1 for r in results if r["status"] == "completed"),
        "job_results": results,
    }


def _extract_files_from_agent_output(output: str) -> list[dict]:
    """Try to parse file list from agent JSON output."""
    # Agent --json wraps response; try to find the code generation JSON inside
    try:
        data = json.loads(output)
        # openclaw agent --json returns {"result": {"content": "..."}, ...}
        content = data.get("result", {}).get("content", "")
        if not content:
            content = output
    except json.JSONDecodeError:
        content = output

    # Try to extract JSON block from content
    for candidate in _find_json_blocks(content):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict) and "files" in parsed:
                return parsed["files"]
        except (json.JSONDecodeError, TypeError):
            continue

    return []


def _find_json_blocks(text: str) -> list[str]:
    """Extract potential JSON blocks from text (fenced or raw)."""
    blocks = []
    # Try fenced code blocks first
    import re
    for match in re.finditer(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL):
        blocks.append(match.group(1).strip())
    # Try the whole text as JSON
    blocks.append(text.strip())
    # Try finding { ... } at top level
    start = text.find("{")
    if start >= 0:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start:i + 1])
                    break
    return blocks


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
                **os.environ,
                "OPENCLAW_BRIDGE_REQUEST_PATH": request_path,
                "OPENCLAW_BRIDGE_RESULT_PATH": result_path,
            },
            capture_output=True,
            text=True,
            timeout=config.openclaw.executor_timeout,
        )

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
