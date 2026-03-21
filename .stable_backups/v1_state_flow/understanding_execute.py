from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.executors.understanding_executor import run_understanding_executor
from app.models.artifact import Artifact
from app.models.execution import Execution
from app.models.goal import Goal
from app.models.outcome import Outcome
from app.models.verification import Verification
from app.services.execution_record_service import (
    create_artifact_record,
    create_execution_record,
    create_verification_record,
    update_outcome_after_execution,
)
from app.verifiers.understanding_verifier import run_understanding_verifier


def _parse_json_like(value: Any) -> Any:
    import json

    if isinstance(value, (dict, list)) or value is None:
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value
        try:
            return json.loads(text)
        except Exception:
            return value
    return value


def _serialize_goal(goal: Goal | None) -> dict[str, Any] | None:
    if not goal:
        return None

    parsed_goal = _parse_json_like(goal.parsed_goal)
    parser_meta = parsed_goal.get("parser_meta") if isinstance(parsed_goal, dict) else None

    return {
        "id": goal.id,
        "raw_input": goal.raw_input,
        "parsed_goal": parsed_goal,
        "goal_type": goal.goal_type,
        "risk_level": goal.risk_level,
        "parser_meta": parser_meta,
        "created_at": goal.created_at,
    }


def _normalize_next_action(value: Any) -> dict[str, Any]:
    parsed = _parse_json_like(value)
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, str):
        return {
            "summary": parsed,
            "step_type": None,
            "steps": [],
            "requires_human_confirmation": False,
        }
    return {
        "summary": None,
        "step_type": None,
        "steps": [],
        "requires_human_confirmation": False,
    }


def _serialize_outcome(outcome: Outcome | None) -> dict[str, Any] | None:
    if not outcome:
        return None

    return {
        "id": outcome.id,
        "goal_id": outcome.goal_id,
        "title": outcome.title,
        "status": outcome.status,
        "current_result": _parse_json_like(outcome.current_result) or {},
        "next_action": _normalize_next_action(outcome.next_action),
        "risk_boundary": outcome.risk_boundary,
        "created_at": outcome.created_at,
        "updated_at": outcome.updated_at,
    }


def _get_goal(db: Session, goal_id: int) -> Goal | None:
    return db.execute(
        select(Goal).where(Goal.id == goal_id)
    ).scalars().first()


def _get_outcome(db: Session, outcome_id: int) -> Outcome | None:
    return db.execute(
        select(Outcome).where(Outcome.id == outcome_id)
    ).scalars().first()


def _get_latest_execution(db: Session, outcome_id: int) -> Execution | None:
    return db.execute(
        select(Execution)
        .where(Execution.outcome_id == outcome_id)
        .order_by(Execution.id.desc())
        .limit(1)
    ).scalars().first()


def _get_latest_artifact(db: Session, outcome_id: int) -> Artifact | None:
    return db.execute(
        select(Artifact)
        .where(Artifact.outcome_id == outcome_id)
        .order_by(Artifact.id.desc())
        .limit(1)
    ).scalars().first()


def _get_latest_verification(db: Session, outcome_id: int) -> Verification | None:
    return db.execute(
        select(Verification)
        .where(Verification.outcome_id == outcome_id)
        .order_by(Verification.id.desc())
        .limit(1)
    ).scalars().first()


def _build_workspace_payload(db: Session, outcome: Outcome) -> dict[str, Any]:
    goal = _get_goal(db, outcome.goal_id)
    latest_outcome = _get_outcome(db, outcome.id)

    return {
        "goal": _serialize_goal(goal),
        "latest_outcome": _serialize_outcome(latest_outcome),
    }


def _has_completed_understanding_result(
    outcome: Outcome,
    execution: Execution | None,
    artifact: Artifact | None,
    verification: Verification | None,
) -> bool:
    current_result = _parse_json_like(outcome.current_result) or {}

    return (
        outcome.status == "completed"
        and execution is not None
        and artifact is not None
        and verification is not None
        and execution.status == "completed"
        and verification.status == "passed"
        and bool(current_result.get("artifact"))
        and bool(current_result.get("verification"))
    )


def execute_outcome_understanding(db: Session, outcome_id: int) -> dict[str, Any]:
    outcome = _get_outcome(db, outcome_id)
    if not outcome:
        return {"detail": f"Outcome {outcome_id} not found"}

    goal = _get_goal(db, outcome.goal_id)
    if not goal:
        return {"detail": f"Goal {outcome.goal_id} not found"}

    existing_execution = _get_latest_execution(db, outcome_id)
    existing_artifact = _get_latest_artifact(db, outcome_id)
    existing_verification = _get_latest_verification(db, outcome_id)

    if _has_completed_understanding_result(
        outcome,
        existing_execution,
        existing_artifact,
        existing_verification,
    ):
        return {
            "execution": {
                "ok": True,
                "goal_id": goal.id,
                "outcome_id": outcome.id,
                "artifact_ref": existing_artifact.artifact_ref,
                "artifact_dir": existing_artifact.file_path,
                "message": "Execution already completed. Returned existing result.",
                "idempotent": True,
            },
            "workspace": _build_workspace_payload(db, outcome),
        }

    executor_result = run_understanding_executor(
        goal_text=goal.raw_input,
        outcome_id=outcome_id,
    )

    artifact_data = executor_result["artifact"]
    ref = artifact_data["artifact_ref"]
    verification_data = run_understanding_verifier(ref=ref)

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
        status="completed",
        current_result=current_result,
        next_action=next_action,
    )

    return {
        "execution": {
            "ok": True,
            "goal_id": goal.id,
            "outcome_id": outcome.id,
            "artifact_ref": artifact_data["artifact_ref"],
            "artifact_dir": artifact_data["file_path"],
            "message": "Understanding execution completed.",
            "idempotent": False,
        },
        "workspace": _build_workspace_payload(db, outcome),
    }
