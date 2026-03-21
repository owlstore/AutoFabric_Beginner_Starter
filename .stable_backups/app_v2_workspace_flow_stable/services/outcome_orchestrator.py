from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.outcome import Outcome
from app.services.executor_bootstrap import bootstrap_executors
from app.services.executor_registry import get_executor

_BOOTSTRAPPED = False


def _ensure_bootstrapped() -> None:
    global _BOOTSTRAPPED
    if not _BOOTSTRAPPED:
        bootstrap_executors()
        _BOOTSTRAPPED = True


def execute_outcome_by_type(db: Session, outcome_id: int) -> dict:
    _ensure_bootstrapped()

    outcome = db.execute(
        select(Outcome).where(Outcome.id == outcome_id)
    ).scalars().first()

    if not outcome:
        return {"detail": f"Outcome {outcome_id} not found"}

    goal = db.execute(
        select(Goal).where(Goal.id == outcome.goal_id)
    ).scalars().first()

    if not goal:
        return {"detail": f"Goal {outcome.goal_id} not found"}

    goal_type = goal.goal_type or "unknown"
    executor = get_executor(goal_type)

    if not executor:
        return {"detail": f"Unsupported goal_type: {goal_type}"}

    return executor(db=db, outcome_id=outcome_id)
