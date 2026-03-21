from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.execution import Execution


router = APIRouter()


def _parse_json_like(value):
    import json
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def serialize_execution(execution: Execution) -> dict:
    return {
        "id": execution.id,
        "outcome_id": execution.outcome_id,
        "executor_name": execution.executor_name,
        "task_name": execution.task_name,
        "status": execution.status,
        "input_payload": _parse_json_like(execution.input_payload),
        "output_payload": _parse_json_like(execution.output_payload),
        "started_at": execution.started_at,
        "finished_at": execution.finished_at,
        "created_at": execution.created_at,
    }


@router.get("/executions")
def list_executions(
    outcome_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    stmt = select(Execution).order_by(desc(Execution.id)).limit(limit)
    if outcome_id is not None:
        stmt = (
            select(Execution)
            .where(Execution.outcome_id == outcome_id)
            .order_by(desc(Execution.id))
            .limit(limit)
        )

    rows = db.execute(stmt).scalars().all()
    return {
        "items": [serialize_execution(row) for row in rows],
        "count": len(rows),
    }
