from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.workspace_service import get_workspace_detail, list_workspaces

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces")
def get_workspaces(
    goal_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    stage: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    items = list_workspaces(
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


@router.get("/workspaces/{goal_id}")
def get_workspace(goal_id: int, db: Session = Depends(get_db)):
    result = get_workspace_detail(db, goal_id=goal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return result
