from __future__ import annotations

from typing import Any


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_detail_sections(
    *,
    goal: dict[str, Any] | None,
    latest_outcome: dict[str, Any] | None,
    executions: list[dict[str, Any]] | None,
    verifications: list[dict[str, Any]] | None,
    artifacts: list[dict[str, Any]] | None,
    flow_events: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    goal = _safe_dict(goal)
    latest_outcome = _safe_dict(latest_outcome)
    current_result = _safe_dict(latest_outcome.get("current_result"))
    next_action = _safe_dict(latest_outcome.get("next_action"))

    sections: list[dict[str, Any]] = []

    sections.append(
        {
            "key": "requirement_card",
            "label": "需求卡",
            "type": "object",
            "visible": True,
            "data": {
                "title": goal.get("title"),
                "goal_type": goal.get("goal_type"),
                "risk_level": goal.get("risk_level"),
                "scope": goal.get("scope"),
                "parser_meta": goal.get("parser_meta"),
                "source_input": goal.get("raw_input"),
                "parsed_goal": goal.get("parsed_goal"),
            },
        }
    )

    sections.append(
        {
            "key": "orchestration_task",
            "label": "编排任务",
            "type": "object",
            "visible": True,
            "data": {
                "stage_key": latest_outcome.get("stage_key"),
                "stage_label": latest_outcome.get("stage_label"),
                "summary": current_result.get("summary"),
                "next_action_summary": next_action.get("summary"),
                "step_type": next_action.get("step_type"),
                "steps": next_action.get("steps"),
                "requires_human_confirmation": next_action.get("requires_human_confirmation"),
                "risk_boundary": latest_outcome.get("risk_boundary"),
            },
        }
    )

    sections.append(
        {
            "key": "execution_records",
            "label": "执行记录",
            "type": "list",
            "visible": True,
            "count": len(executions or []),
            "data": executions or [],
        }
    )

    sections.append(
        {
            "key": "test_summary",
            "label": "测试摘要",
            "type": "list",
            "visible": True,
            "count": len(verifications or []),
            "data": verifications or [],
        }
    )

    sections.append(
        {
            "key": "delivery_summary",
            "label": "交付摘要",
            "type": "object",
            "visible": True,
            "data": {
                "artifact_count": len(artifacts or []),
                "artifacts": artifacts or [],
                "flow_event_count": len(flow_events or []),
                "latest_stage": latest_outcome.get("stage_key"),
                "latest_stage_label": latest_outcome.get("stage_label"),
                "status": latest_outcome.get("status"),
            },
        }
    )

    return sections


def build_stage_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {
        "requirement": 0,
        "clarification": 0,
        "prototype": 0,
        "orchestration": 0,
        "execution": 0,
        "testing": 0,
        "delivery": 0,
        "unknown": 0,
    }

    for item in items:
        stage_key = item.get("stage_key") or item.get("stage") or "unknown"
        if stage_key not in counts:
            stage_key = "unknown"
        counts[stage_key] += 1

    return counts
