from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.artifact import Artifact


router = APIRouter()


def _parse_json_like(value):
    import json
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def serialize_artifact(artifact: Artifact) -> dict:
    return {
        "id": artifact.id,
        "outcome_id": artifact.outcome_id,
        "artifact_type": artifact.artifact_type,
        "file_path": artifact.file_path,
        "artifact_ref": artifact.artifact_ref,
        "metadata": _parse_json_like(getattr(artifact, "artifact_metadata", None)),
        "created_at": artifact.created_at,
    }


@router.get("/artifacts")
def list_artifacts(
    outcome_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    stmt = select(Artifact).order_by(desc(Artifact.id)).limit(limit)
    if outcome_id is not None:
        stmt = (
            select(Artifact)
            .where(Artifact.outcome_id == outcome_id)
            .order_by(desc(Artifact.id))
            .limit(limit)
        )

    rows = db.execute(stmt).scalars().all()
    return {
        "items": [serialize_artifact(row) for row in rows],
        "count": len(rows),
    }
