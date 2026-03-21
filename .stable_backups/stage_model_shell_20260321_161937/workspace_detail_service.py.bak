from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.outcome import Outcome
from app.models.execution import Execution
from app.models.artifact import Artifact
from app.models.verification import Verification
from app.models.flow_event import FlowEvent
from app.services.serializer_service import (
    serialize_goal,
    serialize_outcome,
    serialize_execution,
    serialize_artifact,
    serialize_verification,
    serialize_flow_event,
)


def build_workspace_detail(db: Session, goal_id: int) -> dict | None:
    goal = db.get(Goal, goal_id)
    if not goal:
        return None

    outcomes = db.execute(
        select(Outcome)
        .where(Outcome.goal_id == goal_id)
        .order_by(Outcome.id.desc())
    ).scalars().all()

    outcome_ids = [item.id for item in outcomes]
    latest_outcome = outcomes[0] if outcomes else None

    executions = []
    artifacts = []
    verifications = []
    flow_events = []

    if outcome_ids:
        executions = db.execute(
            select(Execution)
            .where(Execution.outcome_id.in_(outcome_ids))
            .order_by(Execution.id.desc())
        ).scalars().all()

        artifacts = db.execute(
            select(Artifact)
            .where(Artifact.outcome_id.in_(outcome_ids))
            .order_by(Artifact.id.desc())
        ).scalars().all()

        verifications = db.execute(
            select(Verification)
            .where(Verification.outcome_id.in_(outcome_ids))
            .order_by(Verification.id.desc())
        ).scalars().all()

        flow_events = db.execute(
            select(FlowEvent)
            .where(FlowEvent.outcome_id.in_(outcome_ids))
            .order_by(FlowEvent.id.asc())
        ).scalars().all()

    return {
        "goal": serialize_goal(goal),
        "latest_outcome": serialize_outcome(latest_outcome) if latest_outcome else None,
        "outcomes": [serialize_outcome(item) for item in outcomes],
        "executions": [serialize_execution(item) for item in executions],
        "artifacts": [serialize_artifact(item) for item in artifacts],
        "verifications": [serialize_verification(item) for item in verifications],
        "flow_events": [serialize_flow_event(item) for item in flow_events],
        "summary": {
            "goal_id": goal.id,
            "outcome_count": len(outcomes),
            "execution_count": len(executions),
            "artifact_count": len(artifacts),
            "verification_count": len(verifications),
            "flow_event_count": len(flow_events),
            "latest_outcome_status": latest_outcome.status if latest_outcome else None,
            "latest_stage": (
                (latest_outcome.current_result or {}).get("stage")
                if latest_outcome and isinstance(latest_outcome.current_result, dict)
                else None
            ),
        },
    }
