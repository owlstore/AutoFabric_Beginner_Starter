from fastapi import APIRouter
from pydantic import BaseModel

from app.services.manus_workspace_service import (
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
