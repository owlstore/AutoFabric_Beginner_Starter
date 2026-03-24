#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from tool_adapters.execution_runtime import execute_tool_job, resolve_tool_execution
from tool_adapters.runtime_contract import build_tool_receipt, write_tool_receipt


ROOT_DIR = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT_DIR / "runtime"
EXECUTOR_OUTPUT_DIR = RUNTIME_DIR / "executor_outputs"
RUNTIME_STATUS_DIR = RUNTIME_DIR / "openclaw_runtime_status"
BRIDGE_RESULT_DIR = RUNTIME_DIR / "openclaw_bridge_results"

EXECUTOR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RUNTIME_STATUS_DIR.mkdir(parents=True, exist_ok=True)
BRIDGE_RESULT_DIR.mkdir(parents=True, exist_ok=True)


EXECUTOR_SCRIPT_MAP: Dict[str, str] = {
    "requirement_agent": "scripts/executors/requirement_executor.sh",
    "requirement_analyst": "scripts/executors/requirement_executor.sh",
    "clarification_agent": "scripts/executors/clarification_executor.sh",
    "clarification_analyst": "scripts/executors/clarification_executor.sh",
    "prototype_agent": "scripts/executors/prototype_executor.sh",
    "prototype_designer": "scripts/executors/prototype_executor.sh",
    "planner_agent": "scripts/executors/planner_executor.sh",
    "orchestration_planner": "scripts/executors/planner_executor.sh",
    "build_agent": "scripts/executors/build_executor.sh",
    "frontend_builder": "scripts/executors/build_executor.sh",
    "backend_builder": "scripts/executors/build_executor.sh",
    "database_builder": "scripts/executors/build_executor.sh",
    "testing_agent": "scripts/executors/testing_executor.sh",
    "qa_tester": "scripts/executors/testing_executor.sh",
    "delivery_agent": "scripts/executors/delivery_executor.sh",
    "delivery_operator": "scripts/executors/delivery_executor.sh",
    "openclaw_browser_agent": "scripts/executors/browser_executor.sh",
    "openclaw_browser_operator": "scripts/executors/browser_executor.sh",
}


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat()


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_runtime_job(job: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "job_key": str(job.get("key") or ""),
        "job_name": str(job.get("name") or ""),
        "executor": str(job.get("executor") or ""),
        "agent_key": str(job.get("agent_key") or job.get("executor") or ""),
        "required_skills": job.get("required_skills") or [],
        "allowed_tools": job.get("allowed_tools") or [],
        "selected_tool": str(job.get("selected_tool") or ""),
        "selected_tool_name": str(job.get("selected_tool_name") or job.get("selected_tool") or ""),
        "policy_status": str(job.get("policy_status") or "allowed"),
        "blocked_reasons": job.get("blocked_reasons") or [],
        "tool_candidates": job.get("tool_candidates") or [],
        "tool_resolution": job.get("tool_resolution") or {},
        "risk_level": job.get("risk_level"),
        "review_mode": job.get("review_mode"),
        "depends_on": job.get("depends_on") or [],
        "status": "pending",
        "started_at": None,
        "completed_at": None,
        "summary": "",
        "output_file": "",
        "actual_tool": "",
        "actual_tool_name": "",
        "tool_receipt_path": "",
        "tool_probe_status": "",
        "tool_probe_notes": [],
        "tool_adapter_mode": "",
        "tool_adapter_provider": "",
        "tool_adapter_command": "",
        "tool_adapter_intent": "",
        "tool_adapter_fallback_used": False,
    }


def load_executor_output(job_key: str) -> Dict[str, Any]:
    path = EXECUTOR_OUTPUT_DIR / f"{job_key}.json"
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def persist_result(
    result_path: Path,
    bridge_id: str,
    runtime_payload: Dict[str, Any],
    command: str,
) -> None:
    payload = {
        "bridge_id": bridge_id,
        "project_id": runtime_payload.get("project_id"),
        "dispatch_id": runtime_payload.get("dispatch_id"),
        "bridge_status": runtime_payload.get("bridge_status"),
        "runtime_status": runtime_payload.get("runtime_status"),
        "command": command,
        "created_at": utc_now_iso(),
        "jobs": runtime_payload.get("jobs") or [],
        "completed_job_keys": [
            job.get("job_key")
            for job in runtime_payload.get("jobs") or []
            if job.get("status") == "completed"
        ],
        "failed_job_keys": [
            job.get("job_key")
            for job in runtime_payload.get("jobs") or []
            if job.get("status") == "failed"
        ],
        "blocked_job_keys": [
            job.get("job_key")
            for job in runtime_payload.get("jobs") or []
            if job.get("policy_status") == "blocked"
        ],
        "runtime_status_path": runtime_payload.get("runtime_status_path"),
    }
    write_json(result_path, payload)


def persist_executor_output_metadata(runtime_job: Dict[str, Any]) -> None:
    output_file = str(runtime_job.get("output_file") or "").strip()
    if not output_file:
        return

    path = Path(output_file)
    if not path.exists():
        return

    try:
        payload = read_json(path)
    except Exception:
        payload = {}

    payload.update(
        {
            "agent_key": runtime_job.get("agent_key"),
            "skill_keys": runtime_job.get("required_skills") or [],
            "allowed_tools": runtime_job.get("allowed_tools") or [],
            "selected_tool": runtime_job.get("selected_tool") or "",
            "selected_tool_name": runtime_job.get("selected_tool_name") or "",
            "actual_tool": runtime_job.get("actual_tool") or "",
            "actual_tool_name": runtime_job.get("actual_tool_name") or "",
            "policy_status": runtime_job.get("policy_status") or "allowed",
            "blocked_reasons": runtime_job.get("blocked_reasons") or [],
            "tool_receipt_path": runtime_job.get("tool_receipt_path") or "",
            "tool_probe_status": runtime_job.get("tool_probe_status") or "",
            "tool_probe_notes": runtime_job.get("tool_probe_notes") or [],
            "tool_adapter_mode": runtime_job.get("tool_adapter_mode") or "",
            "tool_adapter_provider": runtime_job.get("tool_adapter_provider") or "",
            "tool_adapter_command": runtime_job.get("tool_adapter_command") or "",
            "tool_adapter_intent": runtime_job.get("tool_adapter_intent") or "",
            "tool_adapter_fallback_used": bool(runtime_job.get("tool_adapter_fallback_used")),
        }
    )
    write_json(path, payload)


def persist_tool_receipt(
    runtime_job: Dict[str, Any],
    *,
    phase: str,
    execution_status: str,
    command: str,
    summary: str = "",
) -> None:
    receipt = build_tool_receipt(
        job_key=str(runtime_job.get("job_key") or ""),
        job_name=str(runtime_job.get("job_name") or ""),
        agent_key=str(runtime_job.get("agent_key") or ""),
        selected_tool=str(runtime_job.get("selected_tool") or ""),
        selected_tool_name=str(runtime_job.get("selected_tool_name") or runtime_job.get("selected_tool") or ""),
        phase=phase,
        execution_status=execution_status,
        command=command,
        allowed_tools=list(runtime_job.get("allowed_tools") or []),
        skill_keys=list(runtime_job.get("required_skills") or []),
        policy_status=str(runtime_job.get("policy_status") or "allowed"),
        blocked_reasons=list(runtime_job.get("blocked_reasons") or []),
        output_file=str(runtime_job.get("output_file") or ""),
        summary=summary,
        extra={
            "actual_tool": runtime_job.get("actual_tool") or "",
            "actual_tool_name": runtime_job.get("actual_tool_name") or "",
            "tool_candidates": runtime_job.get("tool_candidates") or [],
            "risk_level": runtime_job.get("risk_level"),
            "review_mode": runtime_job.get("review_mode"),
            "tool_adapter_mode": runtime_job.get("tool_adapter_mode") or "",
            "tool_adapter_provider": runtime_job.get("tool_adapter_provider") or "",
            "tool_adapter_command": runtime_job.get("tool_adapter_command") or "",
            "tool_adapter_intent": runtime_job.get("tool_adapter_intent") or "",
            "tool_adapter_fallback_used": bool(runtime_job.get("tool_adapter_fallback_used")),
        },
    )
    receipt_path = write_tool_receipt(receipt)
    runtime_job["tool_receipt_path"] = receipt_path
    runtime_job["tool_probe_status"] = receipt.get("probe", {}).get("status", "")
    runtime_job["tool_probe_notes"] = receipt.get("probe", {}).get("notes", [])


def main() -> int:
    request_path_raw = os.environ.get("OPENCLAW_BRIDGE_REQUEST_PATH", "").strip()
    bridge_id = os.environ.get("OPENCLAW_BRIDGE_ID", "").strip() or f"bridge_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    runtime_status_path_raw = os.environ.get("OPENCLAW_RUNTIME_STATUS_PATH", "").strip()
    result_path_raw = os.environ.get("OPENCLAW_BRIDGE_RESULT_PATH", "").strip()

    if not request_path_raw:
        print("OPENCLAW_BRIDGE_REQUEST_PATH is empty", file=sys.stderr, flush=True)
        return 1

    request_path = Path(request_path_raw)
    if not request_path.exists():
        print(f"request file not found: {request_path}", file=sys.stderr, flush=True)
        return 1

    runtime_status_path = (
        Path(runtime_status_path_raw)
        if runtime_status_path_raw
        else RUNTIME_STATUS_DIR / f"{bridge_id}.json"
    )
    result_path = (
        Path(result_path_raw)
        if result_path_raw
        else BRIDGE_RESULT_DIR / f"{bridge_id}.json"
    )

    request_payload = read_json(request_path)
    openclaw_payload = request_payload.get("openclaw_payload") or {}
    jobs = openclaw_payload.get("jobs") or []

    runtime_payload: Dict[str, Any] = {
        "bridge_id": bridge_id,
        "project_id": request_payload.get("project_id"),
        "dispatch_id": request_payload.get("dispatch_id"),
        "bridge_status": "running",
        "runtime_status": "pending",
        "job_count": len(jobs),
        "jobs": [build_runtime_job(job) for job in jobs],
        "request_path": str(request_path),
        "runtime_status_path": str(runtime_status_path),
        "started_at": utc_now_iso(),
        "finished_at": None,
    }
    write_json(runtime_status_path, runtime_payload)

    print("==== OpenClaw Bridge Start ====", flush=True)
    print(f"bridge_id: {bridge_id}", flush=True)
    print(f"request_path: {request_path}", flush=True)
    print(f"project_id: {request_payload.get('project_id')}", flush=True)
    print(f"dispatch_id: {request_payload.get('dispatch_id')}", flush=True)
    print(f"job_count: {len(jobs)}", flush=True)
    print("", flush=True)

    command = "python3 scripts/openclaw_bridge_runner.py"

    for index, runtime_job in enumerate(runtime_payload["jobs"], start=1):
        job_key = runtime_job["job_key"]
        job_name = runtime_job["job_name"]
        executor = runtime_job["executor"] or runtime_job["agent_key"]
        script_rel = EXECUTOR_SCRIPT_MAP.get(executor)

        runtime_payload["runtime_status"] = "running"
        runtime_job["status"] = "running"
        runtime_job["started_at"] = utc_now_iso()
        adapter_preview = resolve_tool_execution(runtime_job.get("selected_tool") or "", script_rel, runtime_job)
        runtime_job["tool_adapter_mode"] = adapter_preview.get("mode") or ""
        runtime_job["tool_adapter_provider"] = adapter_preview.get("provider") or ""
        runtime_job["tool_adapter_command"] = adapter_preview.get("command") or ""
        runtime_job["tool_adapter_intent"] = adapter_preview.get("intent") or ""
        runtime_job["tool_adapter_fallback_used"] = bool(adapter_preview.get("fallback_used"))
        runtime_job["tool_probe_status"] = adapter_preview.get("probe_status") or ""
        runtime_job["tool_probe_notes"] = adapter_preview.get("probe_notes") or []
        persist_tool_receipt(
            runtime_job,
            phase="start",
            execution_status="running",
            command=adapter_preview.get("command") or script_rel or "",
            summary="tool adapter receipt created",
        )
        write_json(runtime_status_path, runtime_payload)

        print(
            f"--> START [{index}/{len(jobs)}] {job_key} | {executor} | {job_name}",
            flush=True,
        )
        print(
            f"    depends_on: {','.join(runtime_job.get('depends_on') or []) or '-'}",
            flush=True,
        )

        if not script_rel:
            runtime_job["status"] = "failed"
            runtime_job["completed_at"] = utc_now_iso()
            runtime_job["summary"] = f"unknown executor: {executor}"
            persist_tool_receipt(
                runtime_job,
                phase="finish",
                execution_status="failed",
                command="",
                summary=runtime_job["summary"],
            )
            runtime_payload["bridge_status"] = "failed"
            runtime_payload["runtime_status"] = "failed"
            runtime_payload["finished_at"] = utc_now_iso()
            write_json(runtime_status_path, runtime_payload)
            persist_result(result_path, bridge_id, runtime_payload, command)
            print(f"[bridge] unknown executor: {executor}", file=sys.stderr, flush=True)
            return 1

        if runtime_job.get("policy_status") == "blocked" or not runtime_job.get("selected_tool"):
            runtime_job["status"] = "failed"
            runtime_job["completed_at"] = utc_now_iso()
            runtime_job["summary"] = "策略拒绝执行: " + "; ".join(runtime_job.get("blocked_reasons") or ["未解析到可用工具"])
            persist_tool_receipt(
                runtime_job,
                phase="finish",
                execution_status="blocked",
                command=script_rel,
                summary=runtime_job["summary"],
            )
            runtime_payload["bridge_status"] = "failed"
            runtime_payload["runtime_status"] = "failed"
            runtime_payload["finished_at"] = utc_now_iso()
            write_json(runtime_status_path, runtime_payload)
            persist_result(result_path, bridge_id, runtime_payload, command)
            print(f"[bridge] blocked by policy: {job_key}", file=sys.stderr, flush=True)
            return 1

        execution = execute_tool_job(
            root_dir=ROOT_DIR,
            runtime_job=runtime_job,
            request_payload=request_payload,
            script_rel=script_rel,
        )
        completed = execution["completed"]
        adapter = execution["adapter"]

        if completed.stdout:
            print(completed.stdout.rstrip(), flush=True)
        if completed.stderr:
            print(completed.stderr.rstrip(), file=sys.stderr, flush=True)

        output_payload = execution.get("output_payload") or load_executor_output(job_key)
        runtime_job["output_file"] = execution.get("output_file") or str(EXECUTOR_OUTPUT_DIR / f"{job_key}.json")
        runtime_job["completed_at"] = utc_now_iso()
        runtime_job["actual_tool"] = runtime_job.get("selected_tool") or ""
        runtime_job["actual_tool_name"] = runtime_job.get("selected_tool_name") or runtime_job.get("selected_tool") or ""
        runtime_job["tool_adapter_mode"] = adapter.get("mode") or ""
        runtime_job["tool_adapter_provider"] = adapter.get("provider") or ""
        runtime_job["tool_adapter_command"] = adapter.get("command") or ""
        runtime_job["tool_adapter_intent"] = adapter.get("intent") or ""
        runtime_job["tool_adapter_fallback_used"] = bool(adapter.get("fallback_used"))
        runtime_job["tool_probe_status"] = adapter.get("probe_status") or runtime_job.get("tool_probe_status") or ""
        runtime_job["tool_probe_notes"] = adapter.get("probe_notes") or runtime_job.get("tool_probe_notes") or []
        runtime_job["summary"] = str(
            output_payload.get("summary")
            or completed.stdout.strip()
            or completed.stderr.strip()
            or ""
        )[:500]
        persist_tool_receipt(
            runtime_job,
            phase="finish",
            execution_status="completed" if completed.returncode == 0 else "failed",
            command=script_rel,
            summary=runtime_job["summary"],
        )
        persist_executor_output_metadata(runtime_job)

        if completed.returncode == 0:
            runtime_job["status"] = "completed"
            write_json(runtime_status_path, runtime_payload)
            print(f"<-- DONE  [{index}/{len(jobs)}] {job_key}", flush=True)
            print("", flush=True)
            continue

        runtime_job["status"] = "failed"
        runtime_payload["bridge_status"] = "failed"
        runtime_payload["runtime_status"] = "failed"
        runtime_payload["finished_at"] = utc_now_iso()
        write_json(runtime_status_path, runtime_payload)
        persist_result(result_path, bridge_id, runtime_payload, command)
        print(f"<-- FAIL  [{index}/{len(jobs)}] {job_key}", flush=True)
        return completed.returncode

    runtime_payload["bridge_status"] = "completed"
    runtime_payload["runtime_status"] = "completed"
    runtime_payload["finished_at"] = utc_now_iso()
    write_json(runtime_status_path, runtime_payload)

    subprocess.run(
        ["python3", "scripts/rebuild_autofabric_indexes.py"],
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    subprocess.run(
        ["python3", "scripts/rebuild_autofabric_showcase.py"],
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    persist_result(result_path, bridge_id, runtime_payload, command)

    print("==== Executor outputs =====", flush=True)
    for payload in runtime_payload["jobs"]:
        print(f" - {Path(payload['output_file']).name}", flush=True)
    print("", flush=True)
    print("==== OpenClaw Bridge Done ====", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
