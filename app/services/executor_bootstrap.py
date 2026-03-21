from __future__ import annotations

from app.services.executor_registry import register_executor
from app.services.outcome_execute import execute_outcome_build
from app.services.understanding_execute import execute_outcome_understanding


def bootstrap_executors() -> None:
    register_executor("system_build", execute_outcome_build)
    register_executor("system_understanding", execute_outcome_understanding)
