from __future__ import annotations

from typing import Any


STAGE_LABELS: dict[str, str] = {
    "requirement": "需求阶段",
    "clarification": "澄清阶段",
    "prototype": "原型阶段",
    "orchestration": "编排阶段",
    "execution": "Agent 执行阶段",
    "testing": "测试阶段",
    "delivery": "交付阶段",
    "unknown": "待识别阶段",
}


RAW_STAGE_TO_STAGE_KEY: dict[str, str] = {
    "goal_captured": "requirement",
    "goal_created": "requirement",
    "goal_parsed": "clarification",
    "clarify_goal": "clarification",
    "clarification_needed": "clarification",
    "clarification_completed": "clarification",

    "analysis_context_collected": "clarification",
    "analysis_ready": "clarification",

    "prototype_pending": "prototype",
    "prototype_ready": "prototype",
    "prototype_confirmed": "prototype",

    "orchestration_pending": "orchestration",
    "task_planned": "orchestration",
    "execution_planned": "orchestration",

    "building": "execution",
    "executing": "execution",
    "browser_execution_started": "execution",
    "browser_execution_completed": "execution",
    "execution_completed": "execution",

    "verifying": "testing",
    "verification_started": "testing",
    "verification_completed": "testing",
    "verification_failed": "testing",
    "failed": "testing",
    "pending_review": "testing",

    "ready": "delivery",
    "delivery_ready": "delivery",
    "delivered": "delivery",
    "completed": "delivery",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def map_stage(
    *,
    raw_stage: str | None,
    outcome_status: str | None = None,
    current_result: dict[str, Any] | None = None,
    next_action: dict[str, Any] | None = None,
) -> dict[str, str | None]:
    current_result = _safe_dict(current_result)
    next_action = _safe_dict(next_action)

    candidate = (
        raw_stage
        or current_result.get("stage")
        or next_action.get("stage")
        or outcome_status
        or "unknown"
    )

    stage_key = RAW_STAGE_TO_STAGE_KEY.get(str(candidate), "unknown")

    if stage_key == "unknown":
        text = " ".join(
            str(x)
            for x in [
                raw_stage,
                outcome_status,
                current_result.get("summary"),
                next_action.get("summary"),
                next_action.get("step_type"),
            ]
            if x
        ).lower()

        if any(k in text for k in ["clarify", "澄清", "missing info", "question", "context collected", "analysis context"]):
            stage_key = "clarification"
        elif any(k in text for k in ["prototype", "wireframe", "figma", "原型"]):
            stage_key = "prototype"
        elif any(k in text for k in ["plan", "orchestr", "编排", "route"]):
            stage_key = "orchestration"
        elif any(k in text for k in ["execut", "browser", "agent", "构建", "运行"]):
            stage_key = "execution"
        elif any(k in text for k in ["verify", "test", "验证", "测试"]):
            stage_key = "testing"
        elif any(k in text for k in ["deliver", "delivery", "交付"]):
            stage_key = "delivery"
        elif any(k in text for k in ["goal", "需求", "input"]):
            stage_key = "requirement"

    return {
        "raw_stage": raw_stage,
        "stage_key": stage_key,
        "stage_label": STAGE_LABELS.get(stage_key, STAGE_LABELS["unknown"]),
    }
