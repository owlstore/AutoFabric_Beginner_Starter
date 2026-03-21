from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.outcome import Outcome
from app.services.flow_event_service import create_flow_event_if_status_changed


def _parse_json_like(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def get_outcome_by_id(db: Session, outcome_id: int) -> Outcome | None:
    return db.get(Outcome, outcome_id)


def progress_outcome_state(
    db: Session,
    *,
    outcome_id: int,
    status: str,
    stage: str,
    summary: str,
) -> Outcome:
    outcome = get_outcome_by_id(db, outcome_id)
    if not outcome:
        raise ValueError("Outcome not found")

    old_status = outcome.status

    current_result = _parse_json_like(outcome.current_result) or {}
    current_result["stage"] = stage
    current_result["summary"] = summary

    outcome.status = status
    outcome.current_result = current_result

    create_flow_event_if_status_changed(
        db,
        outcome=outcome,
        old_status=old_status,
        new_status=status,
        trigger_type="manual_progress",
        note=f"Stage updated to {stage}.",
    )

    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome
