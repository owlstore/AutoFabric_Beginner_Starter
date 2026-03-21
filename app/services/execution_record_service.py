from __future__ import annotations

import json
from typing import Any

from app.models.artifact import Artifact
from app.models.execution import Execution
from app.models.outcome import Outcome
from app.models.verification import Verification


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def create_execution_record(db, outcome_id: int, data: dict[str, Any]) -> Execution:
    row = Execution(
        outcome_id=outcome_id,
        executor_name=data["executor_name"],
        task_name=data["task_name"],
        status=data["status"],
        input_payload=_json_text(data["input_payload"]),
        output_payload=_json_text(data["output_payload"]),
        started_at=data.get("started_at"),
        finished_at=data.get("finished_at"),
    )
    db.add(row)
    db.flush()
    return row


def create_artifact_record(db, outcome_id: int, data: dict[str, Any]) -> Artifact:
    row = Artifact(
        outcome_id=outcome_id,
        artifact_type=data["artifact_type"],
        file_path=data["file_path"],
        artifact_ref=data["artifact_ref"],
        artifact_metadata=_json_text(data["artifact_metadata"]),
    )
    db.add(row)
    db.flush()
    return row


def create_verification_record(db, outcome_id: int, data: dict[str, Any]) -> Verification:
    row = Verification(
        outcome_id=outcome_id,
        verifier_name=data["verifier_name"],
        status=data["status"],
        checks=_json_text(data["checks"]),
        summary=_json_text(data["summary"]),
        verified_at=data.get("verified_at"),
    )
    db.add(row)
    db.flush()
    return row


def update_outcome_after_execution(
    db,
    outcome: Outcome,
    *,
    status: str,
    current_result: dict[str, Any],
    next_action: dict[str, Any],
) -> Outcome:
    outcome.status = status
    outcome.current_result = current_result
    outcome.next_action = _json_text(next_action)

    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome
