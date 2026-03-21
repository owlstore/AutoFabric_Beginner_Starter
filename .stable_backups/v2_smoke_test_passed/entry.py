from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.goal_parse_service import parse_goal_input
from app.services.goal_service import create_goal_and_initial_outcome
from app.services.serializer_service import _parse_json_like

router = APIRouter(tags=["entry"])


class EntrySubmitRequest(BaseModel):
    user_input: str
    source_type: str | None = None
    source_ref: str | None = None
    notes: str | None = None


@router.post("/entry/submit")
def submit_entry(payload: EntrySubmitRequest, db: Session = Depends(get_db)):
    raw_input = (payload.user_input or "").strip()

    parse_result = parse_goal_input(raw_input)

    goal, outcome = create_goal_and_initial_outcome(
        db,
        raw_input=raw_input,
        parsed_goal=parse_result["parsed_goal"],
        goal_type=parse_result["goal_type"],
        risk_level=parse_result["risk_level"],
        recommended_next_action=parse_result["recommended_next_action"],
    )

    return {
        "goal_id": goal.id,
        "outcome_id": outcome.id,
        "goal_type": goal.goal_type,
        "risk_level": goal.risk_level,
        "parsed_goal": goal.parsed_goal,
        "next_action": _parse_json_like(outcome.next_action),
    }
