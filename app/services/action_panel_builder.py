from typing import Any


def build_action_panel(
    goal: dict[str, Any],
    latest_outcome: dict[str, Any] | None,
    execution_hint: dict[str, Any] | None,
    recommended_actions: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    if not latest_outcome:
        return []

    parsed_goal = goal.get("parsed_goal") or {}
    intent = parsed_goal.get("intent") or "general_task"
    scope = parsed_goal.get("scope") or "unspecified"
    target = parsed_goal.get("target") or goal.get("raw_input") or "current task"

    next_action = latest_outcome.get("next_action") or {}
    next_summary = next_action.get("summary") or "推进当前结果到下一阶段。"
    step_type = next_action.get("step_type") or "next_step"

    progress_label = _build_progress_label(intent)
    progress_description = next_summary

    panel = [
        {
            "label": progress_label,
            "action_type": "progress_outcome",
            "target": f"/outcomes/{latest_outcome['id']}/progress",
            "priority": "high",
            "description": progress_description,
            "payload_example": {
                "status": "in_progress",
                "stage": "next_stage",
                "summary": f"Progress updated for {target}.",
            },
        }
    ]

    if execution_hint and execution_hint.get("task_example"):
        panel.append(
            {
                "label": _build_executor_label(intent, scope),
                "action_type": "run_executor",
                "target": "/executors/openclaw/run",
                "priority": "high",
                "description": execution_hint.get("reason") or _build_executor_description(intent, scope, target, step_type),
                "payload_example": execution_hint.get("task_example"),
            }
        )

    panel.extend(
        [
            {
                "label": "查看所有结果对象",
                "action_type": "view_outcomes",
                "target": "/outcomes",
                "priority": "low",
                "description": f"查看与 {target} 相关的所有结果对象。",
                "payload_example": None,
            },
            {
                "label": "查看所有目标对象",
                "action_type": "view_goals",
                "target": "/goals",
                "priority": "low",
                "description": f"查看当前系统内所有目标对象，并对比 {target} 的定位。",
                "payload_example": None,
            },
        ]
    )

    return panel


def _build_progress_label(intent: str) -> str:
    if intent == "fix_issue":
        return "推进修复流程"
    if intent == "understand_system":
        return "推进分析阶段"
    if intent == "build_system":
        return "推进构建阶段"
    return "推进到下一阶段"


def _build_executor_label(intent: str, scope: str) -> str:
    if intent == "fix_issue":
        return "调用 OpenClaw 排查问题"
    if intent == "understand_system":
        return "调用 OpenClaw 收集分析上下文"
    if intent == "build_system":
        return "调用 OpenClaw 辅助构建"
    if scope == "frontend":
        return "调用 OpenClaw 检查前端上下文"
    if scope == "backend":
        return "调用 OpenClaw 检查后端上下文"
    return "调用 OpenClaw 执行当前步骤"


def _build_executor_description(intent: str, scope: str, target: str, step_type: str) -> str:
    if intent == "fix_issue":
        return f"围绕 {target} 收集异常信息、定位问题模块，并推进 {step_type}。"
    if intent == "understand_system":
        return f"围绕 {target} 收集结构、依赖与行为信息，辅助建立系统理解。"
    if intent == "build_system":
        return f"围绕 {target} 收集构建所需上下文，辅助定义 MVP 与交付边界。"
    return f"围绕 {target} 执行当前步骤，补充必要上下文。"
