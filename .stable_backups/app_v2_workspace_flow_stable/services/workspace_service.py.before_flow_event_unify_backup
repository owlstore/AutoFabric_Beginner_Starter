from __future__ import annotations

import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.outcome import Outcome
from app.models.flow_event import FlowEvent
from app.services.serializer_service import serialize_goal, serialize_outcome


def _parse_json_like(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def normalize_parsed_goal(parsed_goal: Any) -> dict[str, Any]:
    value = _parse_json_like(parsed_goal)
    return value if isinstance(value, dict) else {}


def normalize_next_action(next_action: Any) -> dict[str, Any] | None:
    value = _parse_json_like(next_action)
    return value if isinstance(value, dict) else None


def serialize_outcome_for_workspace(outcome: Outcome | None) -> dict[str, Any] | None:
    if not outcome:
        return None

    data = serialize_outcome(outcome)
    data["current_result"] = _parse_json_like(data.get("current_result")) or {}
    data["next_action"] = normalize_next_action(data.get("next_action"))
    return data


def _get_latest_outcome(goal: Goal) -> Outcome | None:
    outcomes = list(goal.outcomes or [])
    if not outcomes:
        return None
    outcomes.sort(key=lambda x: x.id)
    return outcomes[-1]


def build_workspace_items(db: Session, limit: int = 20) -> list[dict[str, Any]]:
    goals = db.execute(
        select(Goal).order_by(Goal.id.desc()).limit(limit)
    ).scalars().all()

    items: list[dict[str, Any]] = []

    for goal in goals:
        parsed_goal = normalize_parsed_goal(goal.parsed_goal)
        latest_outcome = _get_latest_outcome(goal)

        flow_event_count = 0
        if latest_outcome:
            flow_event_count = (
                db.execute(
                    select(func.count(FlowEvent.id)).where(
                        FlowEvent.outcome_id == latest_outcome.id
                    )
                ).scalar()
                or 0
            )

        current_result = {}
        next_action = None
        stage = "goal_captured"
        step_type = None
        executor_result_available = False

        if latest_outcome:
            current_result = _parse_json_like(latest_outcome.current_result) or {}
            next_action = normalize_next_action(latest_outcome.next_action)
            stage = current_result.get("stage", "goal_captured")
            step_type = next_action.get("step_type") if next_action else None
            executor_result_available = latest_outcome.status == "completed"

        title = (
            latest_outcome.title
            if latest_outcome and latest_outcome.title
            else parsed_goal.get("target")
            or goal.raw_input
        )

        items.append(
            {
                "goal_id": goal.id,
                "title": title,
                "goal_type": goal.goal_type,
                "risk_level": goal.risk_level,
                "scope": parsed_goal.get("scope", "unspecified"),
                "parser_meta": parsed_goal.get("parser_meta"),
                "stage": stage,
                "step_type": step_type,
                "execution_hint_available": True,
                "executor_touched": executor_result_available,
                "executor_result_available": executor_result_available,
                "recommendation_reason_available": True,
                "flow_event_count": flow_event_count,
                "created_at": goal.created_at,
                "updated_at": latest_outcome.updated_at if latest_outcome else goal.created_at,
                "latest_outcome": serialize_outcome_for_workspace(latest_outcome),
            }
        )

    return items
