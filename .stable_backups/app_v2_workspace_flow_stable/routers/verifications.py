from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.verification import Verification


router = APIRouter()


def _parse_json_like(value):
    import json
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def serialize_verification(verification: Verification) -> dict:
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


@router.get("/verifications")
def list_verifications(
    outcome_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    stmt = select(Verification).order_by(desc(Verification.id)).limit(limit)
    if outcome_id is not None:
        stmt = (
            select(Verification)
            .where(Verification.outcome_id == outcome_id)
            .order_by(desc(Verification.id))
            .limit(limit)
        )

    rows = db.execute(stmt).scalars().all()
    return {
        "items": [serialize_verification(row) for row in rows],
        "count": len(rows),
    }
