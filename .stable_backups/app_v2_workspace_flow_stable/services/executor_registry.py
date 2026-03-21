from __future__ import annotations

from collections.abc import Callable
from typing import Any

ExecutorFunc = Callable[..., dict[str, Any]]

_EXECUTOR_REGISTRY: dict[str, ExecutorFunc] = {}


def register_executor(goal_type: str, executor: ExecutorFunc) -> None:
    _EXECUTOR_REGISTRY[goal_type] = executor


def get_executor(goal_type: str) -> ExecutorFunc | None:
    return _EXECUTOR_REGISTRY.get(goal_type)


def list_registered_goal_types() -> list[str]:
    return sorted(_EXECUTOR_REGISTRY.keys())
