from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.outcome import Outcome
from app.models.artifact import Artifact
from app.models.verification import Verification


def parse_json_like(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            return value
    return value


def ensure_dict(value: Any) -> dict[str, Any]:
    parsed = parse_json_like(value)
    return parsed if isinstance(parsed, dict) else {}


def main() -> None:
    db: Session = SessionLocal()
    updated = 0

    try:
        outcomes = db.execute(
            select(Outcome).where(Outcome.status == "completed").order_by(Outcome.id.asc())
        ).scalars().all()

        for outcome in outcomes:
            artifact = db.execute(
                select(Artifact)
                .where(Artifact.outcome_id == outcome.id)
                .order_by(Artifact.id.desc())
            ).scalars().first()

            verification = db.execute(
                select(Verification)
                .where(Verification.outcome_id == outcome.id)
                .order_by(Verification.id.desc())
            ).scalars().first()

            current_result = ensure_dict(outcome.current_result)
            artifact_meta = ensure_dict(getattr(artifact, "artifact_metadata", None)) if artifact else {}

            has_meaningful_artifact = bool(artifact and artifact.artifact_ref)

            if not has_meaningful_artifact:
                continue

            rebuilt = {
                "stage": "analysis_context_collected",
                "summary": "System understanding context collected.",
                "artifact": {
                    "ref": artifact.artifact_ref,
                    "type": artifact.artifact_type,
                    **artifact_meta,
                },
            }

            if verification:
                rebuilt["verification"] = {
                    "status": verification.status,
                    **(ensure_dict(verification.summary) or {}),
                }

            if current_result != rebuilt:
                outcome.current_result = rebuilt
                db.add(outcome)
                updated += 1

        db.commit()
        print("=== rebuild summary ===")
        print(f"updated={updated}")
        print("rebuild done")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
