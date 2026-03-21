from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.goal import Goal
from app.models.outcome import Outcome
from app.services.serializer_service import (
    serialize_artifact,
    serialize_execution,
    serialize_flow_event,
    serialize_goal,
    serialize_outcome,
    serialize_outcome_for_workspace,
    serialize_verification,
)


def _ensure_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _extract_stage_and_step_type(goal: Goal, latest_outcome: Outcome | None) -> tuple[str, str]:
    parsed_goal = _ensure_dict(goal.parsed_goal)

    if latest_outcome:
        current_result = _ensure_dict(latest_outcome.current_result)
        next_action = _ensure_dict(latest_outcome.next_action)

        stage = current_result.get("stage") or "unknown"
        step_type = next_action.get("step_type") or parsed_goal.get("intent") or "unknown"
        return stage, step_type

    return "unknown", parsed_goal.get("intent") or "unknown"


def list_workspaces(
    db: Session,
    *,
    goal_type: str | None = None,
    status: str | None = None,
    stage: str | None = None,
    risk_level: str | None = None,
) -> list[dict[str, Any]]:
    stmt = (
        select(Goal)
        .options(
            selectinload(Goal.outcomes).selectinload(Outcome.executions),
            selectinload(Goal.outcomes).selectinload(Outcome.artifacts),
            selectinload(Goal.outcomes).selectinload(Outcome.verifications),
            selectinload(Goal.outcomes).selectinload(Outcome.flow_events),
        )
        .order_by(Goal.id.desc())
    )

    goals = db.execute(stmt).scalars().unique().all()

    items: list[dict[str, Any]] = []

    for goal in goals:
        parsed_goal = _ensure_dict(goal.parsed_goal)

        latest_outcome = None
        if goal.outcomes:
            latest_outcome = max(goal.outcomes, key=lambda x: x.id)

        if goal_type and goal.goal_type != goal_type:
            continue

        if risk_level and goal.risk_level != risk_level:
            continue

        if status and (not latest_outcome or latest_outcome.status != status):
            continue

        stage_value, step_type = _extract_stage_and_step_type(goal, latest_outcome)

        if stage and stage_value != stage:
            continue

        executor_result_available = False
        flow_event_count = 0

        if latest_outcome:
            executor_result_available = bool(latest_outcome.executions)
            flow_event_count = len(latest_outcome.flow_events or [])

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
                "stage": stage_value,
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


def get_workspace_detail(db: Session, goal_id: int) -> dict[str, Any] | None:
    stmt = (
        select(Goal)
        .where(Goal.id == goal_id)
        .options(
            selectinload(Goal.outcomes).selectinload(Outcome.executions),
            selectinload(Goal.outcomes).selectinload(Outcome.artifacts),
            selectinload(Goal.outcomes).selectinload(Outcome.verifications),
            selectinload(Goal.outcomes).selectinload(Outcome.flow_events),
        )
    )

    goal = db.execute(stmt).scalars().unique().first()
    if not goal:
        return None

    outcomes = sorted(goal.outcomes or [], key=lambda x: x.id, reverse=True)
    latest_outcome = outcomes[0] if outcomes else None

    return {
        "goal": serialize_goal(goal),
        "latest_outcome": serialize_outcome(latest_outcome) if latest_outcome else None,
        "outcomes": [
            {
                **serialize_outcome(outcome),
                "executions": [serialize_execution(x) for x in outcome.executions],
                "artifacts": [serialize_artifact(x) for x in outcome.artifacts],
                "verifications": [serialize_verification(x) for x in outcome.verifications],
                "timeline": [serialize_flow_event(x) for x in outcome.flow_events],
            }
            for outcome in outcomes
        ],
    }
