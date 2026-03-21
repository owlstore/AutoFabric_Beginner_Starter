from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.flow_event import FlowEvent
from app.models.outcome import Outcome


def create_flow_event(
    db: Session,
    *,
    outcome_id: int,
    from_status: str | None,
    to_status: str,
    trigger_type: str,
    note: str | None = None,
) -> FlowEvent:
    event = FlowEvent(
        outcome_id=outcome_id,
        from_status=from_status,
        to_status=to_status,
        trigger_type=trigger_type,
        note=note,
    )
    db.add(event)
    db.flush()
    return event


def create_flow_event_if_status_changed(
    db: Session,
    *,
    outcome: Outcome,
    old_status: str | None,
    new_status: str,
    trigger_type: str,
    note: str | None = None,
) -> FlowEvent | None:
    if old_status == new_status:
        return None

    return create_flow_event(
        db,
        outcome_id=outcome.id,
        from_status=old_status,
        to_status=new_status,
        trigger_type=trigger_type,
        note=note,
    )
