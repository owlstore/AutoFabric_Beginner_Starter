from __future__ import annotations

import json
from typing import Any


def _infer_step_type(intent: str | None) -> str:
    mapping = {
        "understand_system": "analyze_system",
        "understand_codebase": "analyze_system",
        "fix_bug": "collect_context",
        "build_system": "define_build_scope",
        "clarify_goal": "clarify_goal",
    }
    return mapping.get(intent or "", "collect_context")


def _ensure_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}

    return {}


def build_execution_hint(goal: dict[str, Any], latest_outcome: dict[str, Any] | None) -> dict[str, Any] | None:
    if not goal or not latest_outcome:
        return None

    parsed_goal = _ensure_dict(goal.get("parsed_goal"))
    next_action = _ensure_dict(latest_outcome.get("next_action"))
    current_result = _ensure_dict(latest_outcome.get("current_result"))

    intent = parsed_goal.get("intent")
    scope = parsed_goal.get("scope")
    target = parsed_goal.get("target") or goal.get("raw_input") or "current target"

    step_type = next_action.get("step_type") or _infer_step_type(intent)
    summary = next_action.get("summary") or current_result.get("summary") or "Proceed with the next recommended step."

    reason = f"当前目标是理解 {target}，适合调用执行器补充结构、依赖与行为上下文。"
    if step_type == "define_build_scope":
        reason = f"当前目标围绕 {target}，适合调用执行器补充构建范围、约束与实施上下文。"
    elif step_type == "clarify_goal":
        reason = f"当前目标 {target} 还需要进一步澄清，适合先补充目标上下文再推进。"
    elif step_type == "collect_context":
        reason = f"当前目标与 {target} 相关，适合调用执行器补充决策所需上下文。"

    return {
        "recommended_executor": "openclaw",
        "reason": reason,
        "task_example": {
            "task_name": "collect_system_analysis_context",
            "payload": {
                "goal_id": goal.get("id"),
                "outcome_id": latest_outcome.get("id"),
                "step_type": step_type,
                "action": "collect_system_context",
                "context": {
                    "intent": intent,
                    "scope": scope,
                    "target": target,
                    "summary": summary,
                },
            },
        },
    }