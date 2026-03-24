from fastapi import APIRouter
from pydantic import BaseModel

from app.services.manus_workspace_service import (
    approve_stage,
    bootstrap_project,
    get_workspace_snapshot,
    run_autopilot,
)

router = APIRouter(prefix="/manus", tags=["manus"])


class ManusBootstrapRequest(BaseModel):
    prompt: str
    project_name: str | None = None
    autopilot: bool = True


class ManusAutopilotRequest(BaseModel):
    operator_note: str | None = None


@router.post("/projects/bootstrap")
def bootstrap_manus_project(payload: ManusBootstrapRequest):
    return bootstrap_project(
        prompt=payload.prompt,
        project_name=payload.project_name,
        autopilot=payload.autopilot,
    )


@router.get("/projects/{project_id}/workspace")
def get_manus_workspace(project_id: int):
    return get_workspace_snapshot(project_id)


@router.post("/projects/{project_id}/autopilot")
def continue_manus_project(project_id: int, payload: ManusAutopilotRequest | None = None):
    note = payload.operator_note if payload else None
    return run_autopilot(project_id, operator_note=note)


class ApprovalRequest(BaseModel):
    decision: str = "approved"  # "approved" | "rejected"
    note: str | None = None


@router.post("/projects/{project_id}/approve/{stage_name}")
def approve_project_stage(project_id: int, stage_name: str, payload: ApprovalRequest):
    """Human approves or rejects a stage gate."""
    return approve_stage(project_id, stage_name, decision=payload.decision, note=payload.note)


class RerunRequest(BaseModel):
    note: str | None = None


@router.post("/projects/{project_id}/stages/{stage_name}/rerun")
def rerun_project_stage(project_id: int, stage_name: str, payload: RerunRequest | None = None):
    """Re-run a specific stage and all downstream stages."""
    from app.services.manus_workspace_service import rerun_from_stage
    note = payload.note if payload else None
    return rerun_from_stage(project_id, stage_name, note=note)
