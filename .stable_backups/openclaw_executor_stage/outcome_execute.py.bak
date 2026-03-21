from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.outcome import Outcome
from app.services.flow_event_service import create_flow_event_if_status_changed
from app.services.serializer_service import serialize_goal, serialize_outcome


def _extract_execution_meta(result: dict[str, Any] | None, outcome: Outcome) -> tuple[str | None, str | None]:
    if isinstance(result, dict):
        execution = result.get("execution")
        if isinstance(execution, dict):
            return execution.get("artifact_ref"), execution.get("artifact_dir")

        current_result = result.get("current_result")
        if isinstance(current_result, dict):
            artifact = current_result.get("artifact")
            if isinstance(artifact, dict):
                return artifact.get("ref"), artifact.get("workspace_dir")

    current_result = outcome.current_result if isinstance(outcome.current_result, dict) else {}
    artifact = current_result.get("artifact")
    if isinstance(artifact, dict):
        return artifact.get("ref"), artifact.get("workspace_dir")

    return None, None


def execute_outcome_by_type(db: Session, outcome_id: int) -> dict[str, Any]:
    outcome = db.execute(
        select(Outcome).where(Outcome.id == outcome_id)
    ).scalar_one_or_none()

    if not outcome:
        raise ValueError(f"Outcome not found: {outcome_id}")

    goal = db.execute(
        select(Goal).where(Goal.id == outcome.goal_id)
    ).scalar_one_or_none()

    if not goal:
        raise ValueError(f"Goal not found for outcome: {outcome_id}")

    old_status = outcome.status

    try:
        if goal.goal_type == "system_understanding":
            from app.services.understanding_execute import execute_outcome_understanding

            result = execute_outcome_understanding(db, outcome_id)

        else:
            raise ValueError(f"Unsupported goal_type: {goal.goal_type}")

        db.refresh(outcome)

        create_flow_event_if_status_changed(
            db,
            outcome=outcome,
            old_status=old_status,
            new_status=outcome.status,
            trigger_type="execute_outcome",
            note="Outcome executed by executor.",
        )

        db.commit()
        db.refresh(outcome)

        artifact_ref, artifact_dir = _extract_execution_meta(
            result if isinstance(result, dict) else None,
            outcome,
        )

        if isinstance(result, dict) and "execution" in result and "workspace" in result:
            return result

        return {
            "execution": {
                "ok": True,
                "goal_id": goal.id,
                "outcome_id": outcome.id,
                "artifact_ref": artifact_ref,
                "artifact_dir": artifact_dir,
                "message": "Understanding execution completed.",
                "idempotent": False,
            },
            "workspace": {
                "goal": serialize_goal(goal),
                "latest_outcome": serialize_outcome(outcome),
            },
        }

    except Exception as e:
        db.rollback()
        raise RuntimeError(
            f"execute_outcome_by_type failed: {type(e).__name__}: {e}"
        ) from e
