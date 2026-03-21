from __future__ import annotations

from typing import Any


def parse_goal_input(raw_input: str) -> dict[str, Any]:
    text = (raw_input or "").strip()
    lowered = text.lower()

    goal_type = "general_task"
    risk_level = "low"
    intent = "general_task"
    scope = "unspecified"
    step_type = "clarify_goal"
    summary = "Clarify the request before proceeding."
    steps = [
        "Ask for the desired outcome.",
        "Request relevant system context.",
        "Confirm scope and constraints.",
    ]
    parser_source = "rules_fallback"

    if any(word in lowered for word in ["ubuntu", "docker", "python", "git", "environment", "build"]):
        goal_type = "system_build"
        risk_level = "medium"
        intent = "build_system"
        scope = "infra"
        step_type = "define_build_scope"
        summary = "Define the build scope and prepare the first build outcome."
        steps = [
            "List required tools and versions.",
            "Choose install method and base environment.",
            "Define validation checks for the environment.",
        ]

    elif any(word in lowered for word in ["analyze", "understand", "legacy", "service", "dashboard"]):
        goal_type = "system_understanding"
        risk_level = "medium" if "legacy" in lowered else "low"
        intent = "understand_system"
        scope = (
            "backend" if "backend" in lowered or "service" in lowered
            else "frontend" if "frontend" in lowered or "dashboard" in lowered
            else "unspecified"
        )
        step_type = "analyze_system"
        summary = "Analyze the system and prepare an understanding outcome."
        steps = [
            "Collect project assets",
            "Identify core modules",
            "Document system behavior",
        ]

    elif any(word in lowered for word in ["fix", "bug", "error", "issue", "failure"]):
        goal_type = "bug_fix"
        risk_level = "medium"
        intent = "fix_issue"
        scope = (
            "frontend" if "ui" in lowered or "frontend" in lowered or "dashboard" in lowered
            else "unspecified"
        )
        step_type = "collect_context"
        summary = "Collect error context and prepare a repair outcome."
        steps = [
            "Collect error logs or reproduction context.",
            "Locate the affected module.",
            "Prepare the repair plan and verification path.",
        ]

    parsed_goal = {
        "intent": intent,
        "scope": scope,
        "target": text or "unspecified target",
        "source_text": text,
        "parser_meta": {
            "source": parser_source,
            "llm_enabled": True,
        },
    }

    return {
        "parsed_goal": parsed_goal,
        "goal_type": goal_type,
        "risk_level": risk_level,
        "recommended_next_action": {
            "summary": summary,
            "step_type": step_type,
            "steps": steps,
            "requires_human_confirmation": False,
        },
    }
