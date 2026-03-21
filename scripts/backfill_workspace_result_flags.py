from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.core.db import SessionLocal
from app.models.outcome import Outcome
from app.models.execution import Execution
from app.models.artifact import Artifact
from app.models.verification import Verification


def ensure_dict(value):
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def artifact_payload(artifact: Artifact) -> dict:
    metadata = getattr(artifact, "artifact_metadata", None)
    meta = ensure_dict(metadata)

    result = {
        "ref": artifact.artifact_ref,
        "type": artifact.artifact_type,
    }
    if artifact.file_path:
        if artifact.artifact_type == "analysis_context":
            result["workspace_dir"] = artifact.file_path
        else:
            result["file_path"] = artifact.file_path

    result.update(meta)
    return {k: v for k, v in result.items() if v is not None}


def verification_payload(verification: Verification) -> dict:
    summary = ensure_dict(verification.summary)

    result = {
        "status": verification.status,
    }
    result.update(summary)
    return {k: v for k, v in result.items() if v is not None}


def main():
    db = SessionLocal()
    try:
        outcomes = db.execute(
            select(Outcome).order_by(Outcome.id.asc())
        ).scalars().all()

        updated = 0
        artifact_filled = 0
        verification_filled = 0
        stage_fixed = 0
        summary_fixed = 0

        for outcome in outcomes:
            current_result = ensure_dict(outcome.current_result)

            executions = db.execute(
                select(Execution)
                .where(Execution.outcome_id == outcome.id)
                .order_by(Execution.id.desc())
            ).scalars().all()

            artifacts = db.execute(
                select(Artifact)
                .where(Artifact.outcome_id == outcome.id)
                .order_by(Artifact.id.desc())
            ).scalars().all()

            verifications = db.execute(
                select(Verification)
                .where(Verification.outcome_id == outcome.id)
                .order_by(Verification.id.desc())
            ).scalars().all()

            latest_execution = executions[0] if executions else None
            latest_artifact = artifacts[0] if artifacts else None
            latest_verification = verifications[0] if verifications else None

            changed = False

            if "stage" not in current_result or not current_result.get("stage"):
                if outcome.status == "completed" and latest_artifact:
                    current_result["stage"] = "analysis_context_collected"
                elif outcome.status == "draft":
                    current_result["stage"] = "goal_captured"
                else:
                    current_result["stage"] = "goal_captured"
                stage_fixed += 1
                changed = True

            if "summary" not in current_result or not current_result.get("summary"):
                if outcome.status == "completed" and latest_artifact:
                    current_result["summary"] = "System understanding context collected."
                elif outcome.status == "completed":
                    current_result["summary"] = "Execution completed."
                else:
                    current_result["summary"] = "Goal captured. Execution not started yet."
                summary_fixed += 1
                changed = True

            if latest_artifact and not current_result.get("artifact"):
                current_result["artifact"] = artifact_payload(latest_artifact)
                artifact_filled += 1
                changed = True

            if latest_verification and not current_result.get("verification"):
                current_result["verification"] = verification_payload(latest_verification)
                verification_filled += 1
                changed = True

            if changed:
                outcome.current_result = current_result
                db.add(outcome)
                updated += 1

        db.commit()

        print("=== backfill summary ===")
        print(f"updated={updated}")
        print(f"artifact_filled={artifact_filled}")
        print(f"verification_filled={verification_filled}")
        print(f"stage_fixed={stage_fixed}")
        print(f"summary_fixed={summary_fixed}")
        print("backfill done")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
