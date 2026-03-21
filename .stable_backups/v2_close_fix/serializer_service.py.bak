from __future__ import annotations

import json
from typing import Any

from app.models.goal import Goal
from app.models.outcome import Outcome
from app.models.execution import Execution
from app.models.artifact import Artifact
from app.models.verification import Verification
from app.models.flow_event import FlowEvent


def _parse_json_like(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def serialize_goal(goal: Goal) -> dict[str, Any]:
    parsed_goal = goal.parsed_goal or {}
    return {
        "id": goal.id,
        "raw_input": goal.raw_input,
        "parsed_goal": parsed_goal,
        "goal_type": goal.goal_type,
        "risk_level": goal.risk_level,
        "parser_meta": parsed_goal.get("parser_meta"),
        "created_at": goal.created_at,
    }


def serialize_outcome(outcome: Outcome | None) -> dict[str, Any] | None:
    if not outcome:
        return None

    return {
        "id": outcome.id,
        "goal_id": outcome.goal_id,
        "title": outcome.title,
        "status": outcome.status,
        "current_result": _parse_json_like(outcome.current_result),
        "next_action": _parse_json_like(outcome.next_action),
        "risk_boundary": outcome.risk_boundary,
        "created_at": outcome.created_at,
        "updated_at": outcome.updated_at,
    }


def serialize_outcome_for_workspace(outcome: Outcome | None) -> dict[str, Any] | None:
    return serialize_outcome(outcome)


def serialize_execution(execution: Execution) -> dict[str, Any]:
    return {
        "id": execution.id,
        "outcome_id": execution.outcome_id,
        "executor_name": execution.executor_name,
        "task_name": execution.task_name,
        "status": execution.status,
        "input_payload": _parse_json_like(execution.input_payload),
        "output_payload": _parse_json_like(execution.output_payload),
        "started_at": execution.started_at,
        "finished_at": execution.finished_at,
        "created_at": execution.created_at,
    }


def serialize_artifact(artifact: Artifact) -> dict[str, Any]:
    return {
        "id": artifact.id,
        "outcome_id": artifact.outcome_id,
        "artifact_type": artifact.artifact_type,
        "file_path": artifact.file_path,
        "artifact_ref": artifact.artifact_ref,
        "metadata": _parse_json_like(getattr(artifact, "artifact_metadata", None)),
        "created_at": artifact.created_at,
    }


def serialize_verification(verification: Verification) -> dict[str, Any]:
    return {
        "id": verification.id,
        "outcome_id": verification.outcome_id,
        "verifier_name": verification.verifier_name,
        "status": verification.status,
        "checks": _parse_json_like(verification.checks),
        "summary": _parse_json_like(verification.summary),
        "verified_at": verification.verified_at,
        "created_at": verification.created_at,
    }


def serialize_flow_event(item: FlowEvent) -> dict[str, Any]:
    return {
        "id": item.id,
        "outcome_id": item.outcome_id,
        "from_status": item.from_status,
        "to_status": item.to_status,
        "trigger_type": item.trigger_type,
        "note": item.note,
        "created_at": item.created_at,
    }
