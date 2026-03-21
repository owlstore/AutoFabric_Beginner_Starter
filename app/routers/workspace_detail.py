from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.workspace_detail_service import build_workspace_detail

router = APIRouter(tags=["workspace_detail"])


@router.get("/workspaces/detail/{goal_id}")
def get_workspace_detail(goal_id: int, db: Session = Depends(get_db)):
    result = build_workspace_detail(db, goal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return result
