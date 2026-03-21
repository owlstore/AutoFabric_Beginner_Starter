from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.flow_event import FlowEvent
from app.schemas.workspace import TimelineResponse
from app.services.serializer_service import serialize_flow_event

router = APIRouter(tags=["timeline"])


@router.get("/outcomes/{outcome_id}/timeline", response_model=TimelineResponse)
def get_outcome_timeline(outcome_id: int, db: Session = Depends(get_db)):
    items = db.execute(
        select(FlowEvent)
        .where(FlowEvent.outcome_id == outcome_id)
        .order_by(FlowEvent.id.asc())
    ).scalars().all()

    return {
        "items": [serialize_flow_event(item) for item in items],
        "count": len(items),
    }
