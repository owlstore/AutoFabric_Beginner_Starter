from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.workspace import WorkspaceDetailResponse, WorkspaceListResponse
from app.services.workspace_detail_service import build_workspace_detail
from app.services.workspace_service import build_workspace_items

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces", response_model=WorkspaceListResponse)
def get_workspaces(
    goal_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    stage: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    items = build_workspace_items(
        db,
        goal_type=goal_type,
        status=status,
        stage=stage,
        risk_level=risk_level,
    )
    return {
        "items": items,
        "count": len(items),
        "filters": {
            "goal_type": goal_type,
            "status": status,
            "stage": stage,
            "risk_level": risk_level,
        },
    }


@router.get("/workspaces/detail/{goal_id}", response_model=WorkspaceDetailResponse)
def get_workspace_detail(goal_id: int, db: Session = Depends(get_db)):
    data = build_workspace_detail(db, goal_id)
    if not data:
        return {
            "goal": {
                "id": goal_id,
                "raw_input": "",
                "parsed_goal": {},
                "goal_type": None,
                "risk_level": None,
                "parser_meta": None,
                "created_at": "1970-01-01T00:00:00",
            },
            "latest_outcome": None,
            "outcomes": [],
            "executions": [],
            "artifacts": [],
            "verifications": [],
            "flow_events": [],
            "summary": {
                "goal_id": goal_id,
                "outcome_count": 0,
                "execution_count": 0,
                "artifact_count": 0,
                "verification_count": 0,
                "flow_event_count": 0,
                "latest_outcome_status": None,
                "latest_stage": None,
            },
        }
    return data
