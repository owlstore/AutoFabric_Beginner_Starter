#!/usr/bin/env bash
set -euo pipefail

mkdir -p backend/app/schemas
mkdir -p backend/app/services
mkdir -p backend/app/routers
mkdir -p backend/app/services/autofabric_generated
mkdir -p frontend/src/api
mkdir -p frontend/src/hooks
mkdir -p frontend/src/pages
mkdir -p frontend/src/components/autofabric
mkdir -p docs/autofabric
mkdir -p scripts/executors
mkdir -p runtime/openclaw_dispatches
mkdir -p runtime/openclaw_runtime_status
mkdir -p runtime/openclaw_bridge_requests
mkdir -p runtime/openclaw_bridge_results
mkdir -p runtime/executor_outputs
mkdir -p runtime/generated_build
mkdir -p runtime/testing_reports
mkdir -p runtime/delivery_bundle
mkdir -p runtime/codex_requests
mkdir -p runtime/codex_results
mkdir -p runtime/generated_registry

cat > backend/app/schemas/execution_plan.py <<'PY'
from typing import Any, Dict, List
from pydantic import BaseModel

class AgentJobOut(BaseModel):
    job_key: str
    job_name: str
    stage: str
    executor: str
    input_summary: Dict[str, Any]
    depends_on: List[str]
    status: str

class ExecutionPlanPreviewResponse(BaseModel):
    project_id: int
    orchestration_version: int
    task_count: int
    agent_jobs: List[AgentJobOut]
    execution_plan: Dict[str, Any]
    openclaw_payload: Dict[str, Any]
PY

cat > backend/app/schemas/openclaw_dispatch.py <<'PY'
from typing import Any, Dict
from pydantic import BaseModel

class OpenClawDispatchResponse(BaseModel):
    ok: bool
    project_id: int
    orchestration_version: int
    dispatch_id: str
    dispatch_status: str
    saved_path: str
    job_count: int
    openclaw_payload: Dict[str, Any]
PY

cat > backend/app/schemas/openclaw_dispatch_list.py <<'PY'
from typing import List
from pydantic import BaseModel

class OpenClawDispatchItem(BaseModel):
    dispatch_id: str
    dispatch_status: str
    project_id: int
    orchestration_version: int
    job_count: int
    saved_path: str

class OpenClawDispatchListResponse(BaseModel):
    project_id: int
    items: List[OpenClawDispatchItem]
PY

cat > backend/app/schemas/openclaw_dispatch_detail.py <<'PY'
from typing import Any, Dict
from pydantic import BaseModel

class OpenClawDispatchDetailResponse(BaseModel):
    dispatch_id: str
    dispatch_status: str
    project_id: int
    orchestration_version: int
    job_count: int
    saved_path: str
    openclaw_payload: Dict[str, Any]
PY

cat > backend/app/schemas/openclaw_runtime.py <<'PY'
from typing import Any, Dict, List
from pydantic import BaseModel

class OpenClawRuntimeJobStatus(BaseModel):
    key: str
    name: str
    executor: str
    status: str
    depends_on: List[str]
    inputs: Dict[str, Any]

class OpenClawRuntimeStatusResponse(BaseModel):
    dispatch_id: str
    project_id: int
    runtime_status: str
    job_count: int
    jobs: List[OpenClawRuntimeJobStatus]
    saved_path: str
PY

cat > backend/app/schemas/runtime_stage_sync.py <<'PY'
from typing import List
from pydantic import BaseModel

class RuntimeStageSyncResponse(BaseModel):
    ok: bool
    project_id: int
    current_stage: str
    runtime_status: str
    actions: List[str]
    testing_run_created: bool
    delivery_package_created: bool
    latest_testing_run_id: int | None = None
    latest_delivery_package_id: int | None = None
PY

cat > backend/app/schemas/openclaw_bridge.py <<'PY'
from typing import Any, Dict
from pydantic import BaseModel

class OpenClawBridgeResponse(BaseModel):
    ok: bool
    project_id: int
    dispatch_id: str
    bridge_id: str
    bridge_mode: str
    bridge_status: str
    request_path: str
    result_path: str
    request_payload: Dict[str, Any]
    result_payload: Dict[str, Any]
PY

cat > backend/app/schemas/generated_assets.py <<'PY'
from typing import Dict, List
from pydantic import BaseModel

class GeneratedAssetItem(BaseModel):
    domain: str
    path: str
    file_name: str

class GeneratedAssetsSummaryResponse(BaseModel):
    ok: bool
    counts: Dict[str, int]
    items: List[GeneratedAssetItem]
PY

cat > backend/app/services/execution_plan_service.py <<'PY'
from typing import Any, Dict, List

def choose_executor(task_type: str, task_name: str) -> str:
    task_type = (task_type or "").lower()
    task_name = task_name or ""
    if task_type == "requirement":
        return "requirement_agent"
    if task_type == "clarification":
        return "clarification_agent"
    if task_type == "prototype":
        return "prototype_agent"
    if task_type == "orchestration":
        return "planner_agent"
    if task_type == "testing":
        return "testing_agent"
    if task_type == "delivery":
        return "delivery_agent"
    if task_type == "execution":
        if "页面" in task_name or "浏览器" in task_name:
            return "openclaw_browser_agent"
        return "build_agent"
    return "general_agent"

def build_agent_jobs(task_graph: Dict[str, Any], execution_strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
    tasks = task_graph.get("tasks", []) or []
    task_types = task_graph.get("task_types", []) or []
    jobs: List[Dict[str, Any]] = []
    for index, task_name in enumerate(tasks):
        task_type = task_types[index] if index < len(task_types) else "unknown"
        job_key = f"job_{index + 1:03d}"
        jobs.append(
            {
                "job_key": job_key,
                "job_name": task_name,
                "stage": task_type,
                "executor": choose_executor(task_type, task_name),
                "input_summary": {
                    "task_name": task_name,
                    "task_type": task_type,
                    "execution_mode": execution_strategy.get("mode", "stage-driven"),
                },
                "depends_on": [] if index == 0 else [f"job_{index:03d}"],
                "status": "pending",
            }
        )
    return jobs

def build_execution_plan_preview(project_id: int, orchestration_version: int, task_graph: Dict[str, Any], agent_plan: Dict[str, Any], execution_strategy: Dict[str, Any]) -> Dict[str, Any]:
    agent_jobs = build_agent_jobs(task_graph, execution_strategy)
    execution_plan = {
        "plan_type": "execution-plan-preview",
        "project_id": project_id,
        "orchestration_version": orchestration_version,
        "strategy": execution_strategy,
        "job_sequence": [job["job_key"] for job in agent_jobs],
        "review_mode": execution_strategy.get("review", "human-gate"),
        "total_jobs": len(agent_jobs),
    }
    openclaw_payload = {
        "project_id": project_id,
        "orchestration_version": orchestration_version,
        "source": "autofabric-orchestration-plan",
        "mode": execution_strategy.get("mode", "stage-driven"),
        "review": execution_strategy.get("review", "human-gate"),
        "jobs": [
            {
                "key": job["job_key"],
                "name": job["job_name"],
                "executor": job["executor"],
                "depends_on": job["depends_on"],
                "inputs": job["input_summary"],
            }
            for job in agent_jobs
        ],
        "agent_plan": agent_plan,
    }
    return {
        "project_id": project_id,
        "orchestration_version": orchestration_version,
        "task_count": len(task_graph.get("tasks", []) or []),
        "agent_jobs": agent_jobs,
        "execution_plan": execution_plan,
        "openclaw_payload": openclaw_payload,
    }
PY

cat > backend/app/services/openclaw_worker.py <<'PY'
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

RUNTIME_DIR = Path("runtime/openclaw_dispatches")
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

def choose_executor(task_type: str, task_name: str) -> str:
    task_type = (task_type or "").lower()
    task_name = task_name or ""
    if task_type == "requirement":
        return "requirement_agent"
    if task_type == "clarification":
        return "clarification_agent"
    if task_type == "prototype":
        return "prototype_agent"
    if task_type == "orchestration":
        return "planner_agent"
    if task_type == "testing":
        return "testing_agent"
    if task_type == "delivery":
        return "delivery_agent"
    if task_type == "execution":
        if "页面" in task_name or "浏览器" in task_name:
            return "openclaw_browser_agent"
        return "build_agent"
    return "general_agent"

def build_agent_jobs(task_graph: Dict[str, Any], execution_strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
    tasks = task_graph.get("tasks", []) or []
    task_types = task_graph.get("task_types", []) or []
    jobs: List[Dict[str, Any]] = []
    for index, task_name in enumerate(tasks):
        task_type = task_types[index] if index < len(task_types) else "unknown"
        jobs.append(
            {
                "key": f"job_{index + 1:03d}",
                "name": task_name,
                "executor": choose_executor(task_type, task_name),
                "depends_on": [] if index == 0 else [f"job_{index:03d}"],
                "inputs": {
                    "task_name": task_name,
                    "task_type": task_type,
                    "execution_mode": execution_strategy.get("mode", "stage-driven"),
                },
            }
        )
    return jobs

def build_openclaw_payload(project_id: int, orchestration_version: int, task_graph: Dict[str, Any], agent_plan: Dict[str, Any], execution_strategy: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "project_id": project_id,
        "orchestration_version": orchestration_version,
        "source": "autofabric-orchestration-plan",
        "mode": execution_strategy.get("mode", "stage-driven"),
        "review": execution_strategy.get("review", "human-gate"),
        "submitted_at": datetime.utcnow().isoformat(),
        "jobs": build_agent_jobs(task_graph, execution_strategy),
        "agent_plan": agent_plan,
    }

def dispatch_openclaw_payload(project_id: int, orchestration_version: int, task_graph: Dict[str, Any], agent_plan: Dict[str, Any], execution_strategy: Dict[str, Any]) -> Dict[str, Any]:
    payload = build_openclaw_payload(project_id, orchestration_version, task_graph, agent_plan, execution_strategy)
    dispatch_id = f"oclw_{project_id}_{orchestration_version}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    path = RUNTIME_DIR / f"{dispatch_id}.json"
    saved = {
        "dispatch_id": dispatch_id,
        "dispatch_status": "accepted",
        "project_id": project_id,
        "orchestration_version": orchestration_version,
        "job_count": len(payload.get("jobs", [])),
        "openclaw_payload": payload,
    }
    path.write_text(json.dumps(saved, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "project_id": project_id,
        "orchestration_version": orchestration_version,
        "dispatch_id": dispatch_id,
        "dispatch_status": "accepted",
        "saved_path": str(path),
        "job_count": len(payload.get("jobs", [])),
        "openclaw_payload": payload,
    }
PY

cat > backend/app/services/openclaw_runtime_service.py <<'PY'
import json
from pathlib import Path
from typing import Any, Dict

DISPATCH_DIR = Path("runtime/openclaw_dispatches")
RUNTIME_DIR = Path("runtime/openclaw_runtime_status")
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

def _dispatch_file(dispatch_id: str) -> Path:
    return DISPATCH_DIR / f"{dispatch_id}.json"

def _runtime_file(dispatch_id: str) -> Path:
    return RUNTIME_DIR / f"{dispatch_id}.json"

def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def ensure_runtime_status(dispatch_id: str) -> Dict[str, Any]:
    runtime_path = _runtime_file(dispatch_id)
    if runtime_path.exists():
        return _load_json(runtime_path)
    dispatch_path = _dispatch_file(dispatch_id)
    if not dispatch_path.exists():
        raise FileNotFoundError("dispatch file not found")
    dispatch_payload = _load_json(dispatch_path)
    jobs = dispatch_payload.get("openclaw_payload", {}).get("jobs", [])
    runtime_data = {
        "dispatch_id": dispatch_payload.get("dispatch_id", dispatch_id),
        "project_id": dispatch_payload.get("project_id"),
        "runtime_status": "pending",
        "job_count": len(jobs),
        "jobs": [
            {
                "key": job.get("key"),
                "name": job.get("name"),
                "executor": job.get("executor"),
                "status": "pending",
                "depends_on": job.get("depends_on", []),
                "inputs": job.get("inputs", {}),
            }
            for job in jobs
        ],
    }
    runtime_path.write_text(json.dumps(runtime_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return runtime_data

def get_runtime_status(dispatch_id: str) -> Dict[str, Any]:
    return ensure_runtime_status(dispatch_id)

def simulate_progress(dispatch_id: str) -> Dict[str, Any]:
    runtime_path = _runtime_file(dispatch_id)
    runtime_data = ensure_runtime_status(dispatch_id)
    jobs = runtime_data.get("jobs", [])
    running_job = next((job for job in jobs if job.get("status") == "running"), None)
    if running_job:
        running_job["status"] = "completed"
    else:
        completed_keys = {job["key"] for job in jobs if job.get("status") == "completed"}
        for job in jobs:
            if job.get("status") != "pending":
                continue
            deps = job.get("depends_on", [])
            if all(dep in completed_keys for dep in deps):
                job["status"] = "running"
                break
    statuses = [job.get("status") for job in jobs]
    if jobs and all(status == "completed" for status in statuses):
        runtime_data["runtime_status"] = "completed"
    elif any(status == "running" for status in statuses):
        runtime_data["runtime_status"] = "running"
    else:
        runtime_data["runtime_status"] = "pending"
    runtime_path.write_text(json.dumps(runtime_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return runtime_data
PY

cat > backend/app/services/runtime_stage_sync_service.py <<'PY'
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

RUNTIME_STATUS_DIR = Path("runtime/openclaw_runtime_status")
RUNTIME_STATUS_DIR.mkdir(parents=True, exist_ok=True)

def _utc_now():
    return datetime.utcnow()

def _load_latest_runtime_for_project(project_id: int) -> Optional[Dict[str, Any]]:
    files = sorted(RUNTIME_STATUS_DIR.glob("*.json"), reverse=True)
    for file in files:
        try:
            payload = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if payload.get("project_id") == project_id:
            return payload
    return None

def _get_project(db: Session, project_id: int) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT id, current_stage FROM projects WHERE id = :project_id"),
        {"project_id": project_id},
    ).mappings().first()
    return dict(row) if row else None

def _ensure_stage_row(db: Session, project_id: int, stage_name: str):
    row = db.execute(
        text("SELECT 1 FROM project_stage_states WHERE project_id = :project_id AND stage_name = :stage_name"),
        {"project_id": project_id, "stage_name": stage_name},
    ).mappings().first()
    if not row:
        db.execute(
            text("""
                INSERT INTO project_stage_states
                (project_id, stage_name, stage_status, started_at, completed_at, last_actor, last_note, version_no)
                VALUES (:project_id, :stage_name, 'pending', NULL, NULL, 'system', NULL, 1)
            """),
            {"project_id": project_id, "stage_name": stage_name},
        )

def _transition_stage(db: Session, project_id: int, from_stage: str, to_stage: str, note: str):
    now = _utc_now()
    _ensure_stage_row(db, project_id, from_stage)
    _ensure_stage_row(db, project_id, to_stage)
    db.execute(
        text("""
            UPDATE project_stage_states
            SET stage_status = 'passed', completed_at = :now, last_actor = 'system', last_note = :note
            WHERE project_id = :project_id AND stage_name = :from_stage
        """),
        {"project_id": project_id, "from_stage": from_stage, "note": note, "now": now},
    )
    db.execute(
        text("""
            UPDATE project_stage_states
            SET stage_status = 'in_progress', started_at = COALESCE(started_at, :now), last_actor = 'system', last_note = :note
            WHERE project_id = :project_id AND stage_name = :to_stage
        """),
        {"project_id": project_id, "to_stage": to_stage, "note": note, "now": now},
    )
    db.execute(
        text("UPDATE projects SET current_stage = :to_stage, updated_at = :now WHERE id = :project_id"),
        {"project_id": project_id, "to_stage": to_stage, "now": now},
    )

def _get_latest_testing_run(db: Session, project_id: int):
    row = db.execute(
        text("SELECT id, run_no, status FROM testing_runs WHERE project_id = :project_id ORDER BY run_no DESC, id DESC LIMIT 1"),
        {"project_id": project_id},
    ).mappings().first()
    return dict(row) if row else None

def _get_latest_delivery_package(db: Session, project_id: int):
    row = db.execute(
        text("SELECT id, version_no, status FROM delivery_packages WHERE project_id = :project_id ORDER BY version_no DESC, id DESC LIMIT 1"),
        {"project_id": project_id},
    ).mappings().first()
    return dict(row) if row else None

def _create_testing_run_from_runtime(db: Session, project_id: int, runtime_payload: Dict[str, Any]) -> int:
    latest = _get_latest_testing_run(db, project_id)
    next_run_no = (latest["run_no"] if latest else 0) + 1
    jobs = runtime_payload.get("jobs", []) or []
    completed = sum(1 for j in jobs if j.get("status") == "completed")
    report_json = {
        "source": "runtime-stage-sync",
        "dispatch_id": runtime_payload.get("dispatch_id"),
        "runtime_status": runtime_payload.get("runtime_status"),
        "job_summary": {
            "completed": completed,
            "total": len(jobs),
        },
    }
    row = db.execute(
        text("""
            INSERT INTO testing_runs
            (project_id, run_no, test_summary, test_report_json, pass_count, fail_count, status, created_at, updated_at)
            VALUES
            (:project_id, :run_no, :test_summary, CAST(:test_report_json AS JSONB), :pass_count, :fail_count, :status, :now, :now)
            RETURNING id
        """),
        {
            "project_id": project_id,
            "run_no": next_run_no,
            "test_summary": "基于 OpenClaw runtime 自动生成测试骨架",
            "test_report_json": json.dumps(report_json, ensure_ascii=False),
            "pass_count": completed,
            "fail_count": 0,
            "status": "completed" if runtime_payload.get("runtime_status") == "completed" else "running",
            "now": _utc_now(),
        },
    ).scalar_one()
    return int(row)

def _create_delivery_package_from_runtime(db: Session, project_id: int, runtime_payload: Dict[str, Any]) -> int:
    latest = _get_latest_delivery_package(db, project_id)
    next_version = (latest["version_no"] if latest else 0) + 1
    artifacts_json = [
        {"type": "runtime", "name": runtime_payload.get("dispatch_id", "runtime-dispatch")},
        {"type": "status", "name": runtime_payload.get("runtime_status", "unknown")},
        {"type": "jobs", "name": f'{len(runtime_payload.get("jobs", []) or [])}-jobs'},
    ]
    row = db.execute(
        text("""
            INSERT INTO delivery_packages
            (project_id, version_no, delivery_summary, artifacts_json, release_notes, handoff_notes, status, created_at, updated_at)
            VALUES
            (:project_id, :version_no, :delivery_summary, CAST(:artifacts_json AS JSONB), :release_notes, :handoff_notes, :status, :now, :now)
            RETURNING id
        """),
        {
            "project_id": project_id,
            "version_no": next_version,
            "delivery_summary": "基于 OpenClaw runtime 自动生成交付骨架",
            "artifacts_json": json.dumps(artifacts_json, ensure_ascii=False),
            "release_notes": "系统根据最新 runtime 状态自动生成交付骨架。",
            "handoff_notes": "后续可继续补充真实执行产物、测试证明与交付说明。",
            "status": "ready",
            "now": _utc_now(),
        },
    ).scalar_one()
    return int(row)

def sync_runtime_stage(db: Session, project_id: int) -> Dict[str, Any]:
    project = _get_project(db, project_id)
    if not project:
        raise ValueError("project not found")
    runtime_payload = _load_latest_runtime_for_project(project_id)
    if not runtime_payload:
        raise ValueError("runtime status not found")
    current_stage = project["current_stage"]
    runtime_status = runtime_payload.get("runtime_status", "pending")
    actions = []
    testing_run_created = False
    delivery_package_created = False
    if current_stage == "orchestration" and runtime_status in {"running", "completed"}:
        _transition_stage(db, project_id, "orchestration", "execution", "runtime 已进入执行阶段")
        actions.append("transition: orchestration -> execution")
        current_stage = "execution"
    if current_stage == "execution" and runtime_status == "completed":
        latest_testing = _get_latest_testing_run(db, project_id)
        if not latest_testing:
            _create_testing_run_from_runtime(db, project_id, runtime_payload)
            testing_run_created = True
            actions.append("testing_run_created_from_runtime")
        _transition_stage(db, project_id, "execution", "testing", "execution 完成，自动进入测试阶段")
        actions.append("transition: execution -> testing")
        current_stage = "testing"
    if current_stage == "testing":
        latest_testing = _get_latest_testing_run(db, project_id)
        if latest_testing and latest_testing.get("status") == "completed":
            latest_delivery = _get_latest_delivery_package(db, project_id)
            if not latest_delivery:
                _create_delivery_package_from_runtime(db, project_id, runtime_payload)
                delivery_package_created = True
                actions.append("delivery_package_created_from_runtime")
            _transition_stage(db, project_id, "testing", "delivery", "testing 完成，自动进入交付阶段")
            actions.append("transition: testing -> delivery")
            current_stage = "delivery"
    db.commit()
    latest_testing = _get_latest_testing_run(db, project_id)
    latest_delivery = _get_latest_delivery_package(db, project_id)
    return {
        "ok": True,
        "project_id": project_id,
        "current_stage": current_stage,
        "runtime_status": runtime_status,
        "actions": actions,
        "testing_run_created": testing_run_created,
        "delivery_package_created": delivery_package_created,
        "latest_testing_run_id": latest_testing["id"] if latest_testing else None,
        "latest_delivery_package_id": latest_delivery["id"] if latest_delivery else None,
    }
PY

cat > backend/app/services/openclaw_bridge_service.py <<'PY'
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

DISPATCH_DIR = Path("runtime/openclaw_dispatches")
BRIDGE_REQUEST_DIR = Path("runtime/openclaw_bridge_requests")
BRIDGE_RESULT_DIR = Path("runtime/openclaw_bridge_results")
BRIDGE_REQUEST_DIR.mkdir(parents=True, exist_ok=True)
BRIDGE_RESULT_DIR.mkdir(parents=True, exist_ok=True)

def _utc_now_iso() -> str:
    return datetime.utcnow().isoformat()

def _load_dispatch(dispatch_id: str) -> Dict[str, Any]:
    path = DISPATCH_DIR / f"{dispatch_id}.json"
    if not path.exists():
        raise FileNotFoundError("dispatch file not found")
    return json.loads(path.read_text(encoding="utf-8"))

def _save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def _build_bridge_request(project_id: int, dispatch_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "bridge_version": "v1",
        "submitted_at": _utc_now_iso(),
        "project_id": project_id,
        "dispatch_id": dispatch_payload.get("dispatch_id"),
        "dispatch_status": dispatch_payload.get("dispatch_status"),
        "source": "autofabric-openclaw-bridge",
        "openclaw_payload": dispatch_payload.get("openclaw_payload", {}),
    }

def _run_cli_bridge(command: str, request_path: Path, bridge_id: str) -> Dict[str, Any]:
    env = os.environ.copy()
    env["OPENCLAW_BRIDGE_REQUEST_PATH"] = str(request_path)
    env["OPENCLAW_BRIDGE_ID"] = bridge_id
    completed = subprocess.run(command, shell=True, env=env, capture_output=True, text=True)
    return {
        "bridge_mode": "cli",
        "bridge_status": "completed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "executed_command": command,
    }

def bridge_dispatch_to_openclaw(project_id: int, dispatch_id: str) -> Dict[str, Any]:
    dispatch_payload = _load_dispatch(dispatch_id)
    if dispatch_payload.get("project_id") != project_id:
        raise ValueError("dispatch does not belong to this project")
    bridge_id = f"bridge_{dispatch_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    request_payload = _build_bridge_request(project_id, dispatch_payload)
    request_path = BRIDGE_REQUEST_DIR / f"{bridge_id}.json"
    result_path = BRIDGE_RESULT_DIR / f"{bridge_id}.json"
    _save_json(request_path, request_payload)
    bridge_mode = os.getenv("OPENCLAW_BRIDGE_MODE", "file").strip().lower()
    bridge_cmd = os.getenv("OPENCLAW_BRIDGE_CMD", "").strip()
    if bridge_mode == "cli" and bridge_cmd:
        result_payload = _run_cli_bridge(bridge_cmd, request_path, bridge_id)
    else:
        result_payload = {
            "bridge_mode": "file",
            "bridge_status": "accepted",
            "message": "Bridge request saved. Set OPENCLAW_BRIDGE_MODE=cli and OPENCLAW_BRIDGE_CMD to enable real OpenClaw invocation.",
        }
    _save_json(
        result_path,
        {
            "bridge_id": bridge_id,
            "project_id": project_id,
            "dispatch_id": dispatch_id,
            "request_path": str(request_path),
            "request_payload": request_payload,
            "result_payload": result_payload,
            "created_at": _utc_now_iso(),
        },
    )
    return {
        "ok": True,
        "project_id": project_id,
        "dispatch_id": dispatch_id,
        "bridge_id": bridge_id,
        "bridge_mode": result_payload.get("bridge_mode", bridge_mode),
        "bridge_status": result_payload.get("bridge_status", "accepted"),
        "request_path": str(request_path),
        "result_path": str(result_path),
        "request_payload": request_payload,
        "result_payload": result_payload,
    }
PY

cat > backend/app/services/generated_assets_service.py <<'PY'
import json
from pathlib import Path
from typing import Dict, List

REGISTRY_FILE = Path("runtime/generated_registry/assets_summary.json")
SCAN_RULES = {
    "backend": Path("backend/app/services/autofabric_generated"),
    "frontend": Path("frontend/src/components/autofabric"),
    "docs": Path("docs/autofabric"),
}

def rebuild_generated_assets_registry() -> Dict:
    items: List[Dict] = []
    for domain, base in SCAN_RULES.items():
        base.mkdir(parents=True, exist_ok=True)
        for file in sorted(base.rglob("*")):
            if file.is_file():
                items.append({"domain": domain, "path": str(file), "file_name": file.name})
    counts = {
        "backend": sum(1 for x in items if x["domain"] == "backend"),
        "frontend": sum(1 for x in items if x["domain"] == "frontend"),
        "docs": sum(1 for x in items if x["domain"] == "docs"),
        "total": len(items),
    }
    payload = {"ok": True, "counts": counts, "items": items}
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload

def get_generated_assets_summary() -> Dict:
    if not REGISTRY_FILE.exists():
        return rebuild_generated_assets_registry()
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return rebuild_generated_assets_registry()
PY

cat > backend/app/routers/execution_plan_router.py <<'PY'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.execution_plan import ExecutionPlanPreviewResponse
from backend.app.services.execution_plan_service import build_execution_plan_preview

router = APIRouter(prefix="/projects", tags=["execution-plan"])

@router.get("/{project_id}/execution-plan-preview", response_model=ExecutionPlanPreviewResponse)
def get_execution_plan_preview(project_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            SELECT id, version_no, task_graph_json, agent_plan_json, execution_strategy_json
            FROM orchestration_plans
            WHERE project_id = :project_id
            ORDER BY version_no DESC, id DESC
            LIMIT 1
        """),
        {"project_id": project_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="No orchestration plan found for this project")
    return build_execution_plan_preview(
        project_id=project_id,
        orchestration_version=row["version_no"] or 1,
        task_graph=row["task_graph_json"] or {},
        agent_plan=row["agent_plan_json"] or {},
        execution_strategy=row["execution_strategy_json"] or {},
    )
PY

cat > backend/app/routers/openclaw_dispatch_router.py <<'PY'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.openclaw_dispatch import OpenClawDispatchResponse
from backend.app.services.openclaw_worker import dispatch_openclaw_payload

router = APIRouter(prefix="/projects", tags=["openclaw-dispatch"])

@router.post("/{project_id}/dispatch-openclaw", response_model=OpenClawDispatchResponse)
def dispatch_openclaw(project_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            SELECT id, version_no, task_graph_json, agent_plan_json, execution_strategy_json
            FROM orchestration_plans
            WHERE project_id = :project_id
            ORDER BY version_no DESC, id DESC
            LIMIT 1
        """),
        {"project_id": project_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="No orchestration plan found for this project")
    return dispatch_openclaw_payload(
        project_id=project_id,
        orchestration_version=row["version_no"] or 1,
        task_graph=row["task_graph_json"] or {},
        agent_plan=row["agent_plan_json"] or {},
        execution_strategy=row["execution_strategy_json"] or {},
    )
PY

cat > backend/app/routers/openclaw_dispatch_query_router.py <<'PY'
import json
from pathlib import Path
from fastapi import APIRouter
from backend.app.schemas.openclaw_dispatch_list import OpenClawDispatchItem, OpenClawDispatchListResponse

router = APIRouter(prefix="/projects", tags=["openclaw-dispatch-query"])
RUNTIME_DIR = Path("runtime/openclaw_dispatches")

@router.get("/{project_id}/openclaw-dispatches", response_model=OpenClawDispatchListResponse)
def list_openclaw_dispatches(project_id: int):
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for file in sorted(RUNTIME_DIR.glob("*.json"), reverse=True):
        try:
            payload = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if payload.get("project_id") != project_id:
            continue
        items.append(
            OpenClawDispatchItem(
                dispatch_id=payload.get("dispatch_id", file.stem),
                dispatch_status=payload.get("dispatch_status", "unknown"),
                project_id=payload.get("project_id", project_id),
                orchestration_version=payload.get("orchestration_version", 0),
                job_count=payload.get("job_count", 0),
                saved_path=str(file),
            )
        )
    return OpenClawDispatchListResponse(project_id=project_id, items=items)
PY

cat > backend/app/routers/openclaw_dispatch_detail_router.py <<'PY'
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.app.schemas.openclaw_dispatch_detail import OpenClawDispatchDetailResponse

router = APIRouter(prefix="/projects", tags=["openclaw-dispatch-detail"])
RUNTIME_DIR = Path("runtime/openclaw_dispatches")

@router.get("/{project_id}/openclaw-dispatches/{dispatch_id}", response_model=OpenClawDispatchDetailResponse)
def get_openclaw_dispatch_detail(project_id: int, dispatch_id: str):
    file_path = RUNTIME_DIR / f"{dispatch_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dispatch not found")
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        raise HTTPException(status_code=500, detail="Dispatch file is invalid")
    if payload.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail="Dispatch does not belong to this project")
    return OpenClawDispatchDetailResponse(
        dispatch_id=payload.get("dispatch_id", dispatch_id),
        dispatch_status=payload.get("dispatch_status", "unknown"),
        project_id=payload.get("project_id", project_id),
        orchestration_version=payload.get("orchestration_version", 0),
        job_count=payload.get("job_count", 0),
        saved_path=str(file_path),
        openclaw_payload=payload.get("openclaw_payload", {}),
    )
PY

cat > backend/app/routers/openclaw_runtime_router.py <<'PY'
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.app.schemas.openclaw_runtime import OpenClawRuntimeStatusResponse
from backend.app.services.openclaw_runtime_service import get_runtime_status, simulate_progress

router = APIRouter(prefix="/projects", tags=["openclaw-runtime"])

@router.get("/{project_id}/openclaw-dispatches/{dispatch_id}/runtime-status", response_model=OpenClawRuntimeStatusResponse)
def read_runtime_status(project_id: int, dispatch_id: str):
    try:
        data = get_runtime_status(dispatch_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    if data.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail="Dispatch does not belong to this project")
    return {**data, "saved_path": str(Path("runtime/openclaw_runtime_status") / f"{dispatch_id}.json")}

@router.post("/{project_id}/openclaw-dispatches/{dispatch_id}/simulate-progress", response_model=OpenClawRuntimeStatusResponse)
def push_runtime_progress(project_id: int, dispatch_id: str):
    try:
        data = simulate_progress(dispatch_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    if data.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail="Dispatch does not belong to this project")
    return {**data, "saved_path": str(Path("runtime/openclaw_runtime_status") / f"{dispatch_id}.json")}
PY

cat > backend/app/routers/runtime_stage_sync_router.py <<'PY'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.runtime_stage_sync import RuntimeStageSyncResponse
from backend.app.services.runtime_stage_sync_service import sync_runtime_stage

router = APIRouter(prefix="/projects", tags=["runtime-stage-sync"])

@router.post("/{project_id}/sync-runtime-stage", response_model=RuntimeStageSyncResponse)
def sync_runtime_stage_endpoint(project_id: int, db: Session = Depends(get_db)):
    try:
        return sync_runtime_stage(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
PY

cat > backend/app/routers/openclaw_bridge_router.py <<'PY'
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.app.schemas.openclaw_bridge import OpenClawBridgeResponse
from backend.app.services.openclaw_bridge_service import bridge_dispatch_to_openclaw

router = APIRouter(prefix="/projects", tags=["openclaw-bridge"])
DISPATCH_DIR = Path("runtime/openclaw_dispatches")

def _find_latest_dispatch_for_project(project_id: int) -> str | None:
    files = sorted(DISPATCH_DIR.glob("*.json"), reverse=True)
    for file in files:
        try:
            payload = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if payload.get("project_id") == project_id:
            return payload.get("dispatch_id")
    return None

@router.post("/{project_id}/bridge-openclaw", response_model=OpenClawBridgeResponse)
def bridge_openclaw(project_id: int):
    dispatch_id = _find_latest_dispatch_for_project(project_id)
    if not dispatch_id:
        raise HTTPException(status_code=404, detail="No dispatch found for this project")
    try:
        return bridge_dispatch_to_openclaw(project_id, dispatch_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dispatch file not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
PY

cat > backend/app/routers/generated_assets_router.py <<'PY'
from fastapi import APIRouter
from backend.app.schemas.generated_assets import GeneratedAssetsSummaryResponse
from backend.app.services.generated_assets_service import get_generated_assets_summary, rebuild_generated_assets_registry

router = APIRouter(tags=["generated-assets"])

@router.get("/generated-assets/summary", response_model=GeneratedAssetsSummaryResponse)
def get_generated_assets():
    return get_generated_assets_summary()

@router.post("/generated-assets/rebuild", response_model=GeneratedAssetsSummaryResponse)
def rebuild_generated_assets():
    return rebuild_generated_assets_registry()
PY

cat > backend/app/routers/autofabric_generated_router.py <<'PY'
from importlib import import_module
from fastapi import APIRouter

router = APIRouter(prefix="/autofabric", tags=["autofabric-generated"])

@router.get("/services")
def list_autofabric_services():
    try:
        registry_module = import_module("backend.app.services.autofabric_generated.registry")
        registry = getattr(registry_module, "AUTOFABRIC_SERVICE_REGISTRY", {})
    except Exception as exc:
        return {"ok": False, "error": str(exc), "services": []}
    return {"ok": True, "count": len(registry), "services": sorted(list(registry.keys()))}
PY

python3 - <<'PY'
from pathlib import Path

main_file = Path("backend/app/main.py")
text = main_file.read_text(encoding="utf-8")

imports = [
    "from backend.app.routers.execution_plan_router import router as execution_plan_router",
    "from backend.app.routers.openclaw_dispatch_router import router as openclaw_dispatch_router",
    "from backend.app.routers.openclaw_dispatch_query_router import router as openclaw_dispatch_query_router",
    "from backend.app.routers.openclaw_dispatch_detail_router import router as openclaw_dispatch_detail_router",
    "from backend.app.routers.openclaw_runtime_router import router as openclaw_runtime_router",
    "from backend.app.routers.runtime_stage_sync_router import router as runtime_stage_sync_router",
    "from backend.app.routers.openclaw_bridge_router import router as openclaw_bridge_router",
    "from backend.app.routers.generated_assets_router import router as generated_assets_router",
    "from backend.app.routers.autofabric_generated_router import router as autofabric_generated_router",
]
includes = [
    "app.include_router(execution_plan_router)",
    "app.include_router(openclaw_dispatch_router)",
    "app.include_router(openclaw_dispatch_query_router)",
    "app.include_router(openclaw_dispatch_detail_router)",
    "app.include_router(openclaw_runtime_router)",
    "app.include_router(runtime_stage_sync_router)",
    "app.include_router(openclaw_bridge_router)",
    "app.include_router(generated_assets_router)",
    "app.include_router(autofabric_generated_router)",
]

lines = text.splitlines()
for imp in imports:
    if imp not in text:
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                insert_at = i + 1
        lines.insert(insert_at, imp)
        text = "\n".join(lines)
        lines = text.splitlines()

for inc in includes:
    if inc not in text:
        idxs = [i for i, line in enumerate(lines) if "app.include_router(" in line]
        if idxs:
            lines.insert(idxs[-1] + 1, inc)
        else:
            lines.append(inc)
        text = "\n".join(lines)
        lines = text.splitlines()

main_file.write_text(text + "\n", encoding="utf-8")
print("已补齐 backend/app/main.py routers")
PY

cat > scripts/executors/requirement_executor.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
JOB_KEY="${JOB_KEY:-unknown}"
JOB_NAME="${JOB_NAME:-unknown}"
OUT="runtime/executor_outputs/${JOB_KEY}.json"
cat > "$OUT" <<EOF
{
  "job_key": "$JOB_KEY",
  "executor": "requirement_agent",
  "job_name": "$JOB_NAME",
  "status": "completed",
  "summary": "已生成需求卡骨架"
}
EOF
echo "[requirement_agent] completed -> $JOB_KEY"
