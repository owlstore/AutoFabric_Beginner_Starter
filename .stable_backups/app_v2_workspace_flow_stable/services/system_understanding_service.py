from __future__ import annotations

import importlib
import inspect
from typing import Any


def _pick_kwargs(callable_obj, source_kwargs: dict[str, Any]) -> dict[str, Any]:
    sig = inspect.signature(callable_obj)
    accepted: dict[str, Any] = {}

    for name, param in sig.parameters.items():
        if name in source_kwargs:
            accepted[name] = source_kwargs[name]

    return accepted


def _normalize_result(result: Any, outcome: Any, target: str) -> dict[str, Any]:
    if isinstance(result, dict):
        if "summary" in result or "artifact" in result or "verification" in result:
            return {
                "summary": result.get("summary", "System understanding context collected."),
                "artifact": result.get("artifact"),
                "verification": result.get("verification"),
            }

        workspace = result.get("workspace")
        if isinstance(workspace, dict):
            latest_outcome = workspace.get("latest_outcome")
            if isinstance(latest_outcome, dict):
                current_result = latest_outcome.get("current_result")
                if isinstance(current_result, dict):
                    return {
                        "summary": current_result.get("summary", "System understanding context collected."),
                        "artifact": current_result.get("artifact"),
                        "verification": current_result.get("verification"),
                    }

        execution = result.get("execution")
        if isinstance(execution, dict):
            return {
                "summary": "System understanding context collected.",
                "artifact": {
                    "ref": execution.get("artifact_ref"),
                    "type": "analysis_context",
                    "workspace_dir": execution.get("artifact_dir"),
                },
                "verification": {
                    "status": "passed" if execution.get("artifact_ref") or execution.get("artifact_dir") else "unknown",
                    "ref": execution.get("artifact_ref"),
                },
            }

    return {
        "summary": "System understanding context collected.",
        "artifact": None,
        "verification": None,
    }


def _try_module_functions(module, kwargs: dict[str, Any], errors: list[str]):
    function_candidates = [
        "collect_system_context",
        "execute_understanding",
        "execute_understanding_outcome",
        "run_understanding",
        "run_understanding_execution",
        "execute",
        "run",
    ]

    for func_name in function_candidates:
        func = getattr(module, func_name, None)
        if not callable(func):
            continue

        try:
            call_kwargs = _pick_kwargs(func, kwargs)
            result = func(**call_kwargs)
            return result
        except Exception as e:
            errors.append(f"{module.__name__}.{func_name} failed: {e}")

    return None


def _try_executor_classes(module, kwargs: dict[str, Any], errors: list[str]):
    class_candidates = [
        "UnderstandingExecutor",
        "SystemUnderstandingExecutor",
    ]
    method_candidates = [
        "collect_system_context",
        "execute_understanding",
        "execute_understanding_outcome",
        "run_understanding",
        "run_understanding_execution",
        "execute",
        "run",
    ]

    for class_name in class_candidates:
        cls = getattr(module, class_name, None)
        if cls is None:
            continue

        try:
            instance = cls()
        except Exception as e:
            errors.append(f"{module.__name__}.{class_name} init failed: {e}")
            continue

        for method_name in method_candidates:
            method = getattr(instance, method_name, None)
            if not callable(method):
                continue

            try:
                call_kwargs = _pick_kwargs(method, kwargs)
                result = method(**call_kwargs)
                return result
            except Exception as e:
                errors.append(f"{module.__name__}.{class_name}.{method_name} failed: {e}")

    return None


def collect_system_context(db, outcome, target: str) -> dict[str, Any]:
    kwargs = {
        "db": db,
        "session": db,
        "outcome": outcome,
        "target": target,
        "goal_id": getattr(outcome, "goal_id", None),
        "outcome_id": getattr(outcome, "id", None),
        "workspace_dir": None,
        "project_path": None,
    }

    module_candidates = [
        "app.services.understanding_execute",
        "app.executors.understanding_executor",
    ]

    errors: list[str] = []

    for mod_name in module_candidates:
        try:
            module = importlib.import_module(mod_name)
        except Exception as e:
            errors.append(f"{mod_name} import failed: {e}")
            continue

        result = _try_module_functions(module, kwargs, errors)
        if result is not None:
            return _normalize_result(result, outcome, target)

        result = _try_executor_classes(module, kwargs, errors)
        if result is not None:
            return _normalize_result(result, outcome, target)

    joined = "\n".join(errors) if errors else "No callable implementation found."
    raise RuntimeError(
        "collect_system_context adapter failed.\n" + joined
    )
