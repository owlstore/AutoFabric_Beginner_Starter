from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.executors.openclaw_executor import run_openclaw_task
from app.models.goal import Goal
from app.models.outcome import Outcome
from app.services.execution_record_service import (
    create_artifact_record,
    create_execution_record,
    create_verification_record,
    update_outcome_after_execution,
)
from app.services.serializer_service import serialize_goal, serialize_outcome
from app.verifiers.openclaw_verifier import run_openclaw_verifier


def execute_outcome_openclaw(
    db: Session,
    outcome_id: int,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = payload or {}

    outcome = db.execute(
        select(Outcome).where(Outcome.id == outcome_id)
    ).scalar_one_or_none()
    if not outcome:
        return {"detail": f"Outcome {outcome_id} not found"}

    goal = db.execute(
        select(Goal).where(Goal.id == outcome.goal_id)
    ).scalar_one_or_none()
    if not goal:
        return {"detail": f"Goal {outcome.goal_id} not found"}

    task_name = payload.get("task_name") or f"goal_{goal.goal_type or 'openclaw'}"
    openclaw_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}

    merged_payload = {
        "goal_id": goal.id,
        "outcome_id": outcome.id,
        "goal_type": goal.goal_type,
        "goal_text": goal.raw_input,
        "parsed_goal": goal.parsed_goal,
        **openclaw_payload,
    }

    executor_result = run_openclaw_task(
        task_name=task_name,
        payload=merged_payload,
        outcome_id=outcome_id,
    )

    artifact_data = executor_result["artifact"]
    verification_data = run_openclaw_verifier(
        executor_result=executor_result,
        artifact_ref=artifact_data["artifact_ref"],
    )

    current_result = executor_result["current_result"]
    current_result["verification"] = verification_data["current_result_verification"]
    next_action = verification_data["next_action"]

    create_execution_record(
        db,
        outcome.id,
        {
            "executor_name": executor_result["executor_name"],
            "task_name": executor_result["task_name"],
            "status": executor_result["status"],
            "input_payload": executor_result["input_payload"],
            "output_payload": executor_result["output_payload"],
            "started_at": None,
            "finished_at": None,
        },
    )

    create_artifact_record(
        db,
        outcome.id,
        artifact_data,
    )

    create_verification_record(
        db,
        outcome.id,
        {
            "verifier_name": verification_data["verifier_name"],
            "status": verification_data["status"],
            "checks": verification_data["checks"],
            "summary": verification_data["summary"],
            "verified_at": None,
        },
    )

    outcome = update_outcome_after_execution(
        db,
        outcome,
        status="completed" if verification_data["status"] == "passed" else "failed",
        current_result=current_result,
        next_action=next_action,
    )

    return {
        "execution": {
            "ok": verification_data["status"] == "passed",
            "goal_id": goal.id,
            "outcome_id": outcome.id,
            "artifact_ref": artifact_data["artifact_ref"],
            "artifact_dir": artifact_data["file_path"],
            "message": "OpenClaw execution completed."
            if verification_data["status"] == "passed"
            else "OpenClaw execution failed.",
            "idempotent": False,
            "executor_type": "openclaw",
            "task_name": task_name,
        },
        "workspace": {
            "goal": serialize_goal(goal),
            "latest_outcome": serialize_outcome(outcome),
        },
    }
