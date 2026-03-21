from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.outcome_service import progress_outcome_state
from app.services.outcome_execute import execute_outcome_by_type
from app.utils.outcome_serializer import serialize_outcome


router = APIRouter()


@router.post("/outcomes/{outcome_id}/progress")
def progress_outcome(outcome_id: int, payload: dict, db: Session = Depends(get_db)):
    status = (payload or {}).get("status", "in_progress")
    stage = (payload or {}).get("stage", "next_stage")
    summary = (payload or {}).get("summary", "Outcome progressed.")

    try:
        outcome = progress_outcome_state(
            db=db,
            outcome_id=outcome_id,
            status=status,
            stage=stage,
            summary=summary,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    return {
        "ok": True,
        "outcome": serialize_outcome(outcome),
    }


@router.post("/outcomes/{outcome_id}/execute")
def execute_outcome(outcome_id: int, payload: dict | None = None, db: Session = Depends(get_db)):
    payload = payload or {}
    executor_type = payload.get("executor_type")

    result = execute_outcome_by_type(
        db=db,
        outcome_id=outcome_id,
        executor_type=executor_type,
        payload=payload,
    )

    if result.get("detail"):
        detail = result["detail"]
        if "not found" in str(detail).lower():
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)

    return jsonable_encoder(result)
