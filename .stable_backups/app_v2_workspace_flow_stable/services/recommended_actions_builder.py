from typing import Any

def build_recommended_actions(goal: dict[str, Any], outcome: dict[str, Any] | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []

    if not outcome:
        actions.append({
            "label": "创建第一条结果对象",
            "action_type": "create_outcome",
            "target": "/outcomes"
        })
        return actions

    outcome_id = outcome.get("id")
    status = outcome.get("status")
    next_action = outcome.get("next_action") or {}
    step_type = next_action.get("step_type") if isinstance(next_action, dict) else None

    if status == "draft":
        actions.append({
            "label": "启动结果推进",
            "action_type": "progress_outcome",
            "target": f"/outcomes/{outcome_id}/progress"
        })

    if status == "in_progress":
        actions.append({
            "label": "推进到下一阶段",
            "action_type": "progress_outcome",
            "target": f"/outcomes/{outcome_id}/progress"
        })

    if step_type in {"locate_module", "inspect_logs", "define_build_scope", "analyze_system"}:
        actions.append({
            "label": "调用 OpenClaw 执行当前步骤",
            "action_type": "run_executor",
            "target": "/executors/openclaw/run"
        })

    actions.append({
        "label": "查看所有结果对象",
        "action_type": "view_outcomes",
        "target": "/outcomes"
    })

    actions.append({
        "label": "查看所有目标对象",
        "action_type": "view_goals",
        "target": "/goals"
    })

    return actions
