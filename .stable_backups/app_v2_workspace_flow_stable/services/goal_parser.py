from typing import Any

from app.services.llm_goal_parser import parse_goal_with_llm, is_llm_enabled


ALLOWED_SCOPES = {"frontend", "backend", "infra", "data", "unspecified"}
ALLOWED_GOAL_TYPES = {"bug_fix", "system_understanding", "system_build", "general_task"}
ALLOWED_RISK_LEVELS = {"low", "medium", "high"}
ALLOWED_STEP_TYPES = {"collect_context", "analyze_system", "define_build_scope", "clarify_goal"}


def parse_goal_from_text(user_input: str) -> dict[str, Any]:
    user_input = user_input.strip()

    parsed: dict[str, Any]
    parser_source = "rules_fallback"

    if is_llm_enabled():
        try:
            parsed = parse_goal_with_llm(user_input)
            parser_source = "llm"
        except Exception as e:
            print("GOAL_PARSER_FALLBACK_REASON =", repr(e))
            parsed = _parse_goal_with_rules(user_input)
            parser_source = "rules_fallback"
    else:
        print("GOAL_PARSER_FALLBACK_REASON = 'LLM disabled or missing key'")
        parsed = _parse_goal_with_rules(user_input)
        parser_source = "rules_fallback"

    normalized = _normalize_parsed_goal(parsed, user_input)
    normalized["parser_meta"] = {
        "source": parser_source,
        "llm_enabled": is_llm_enabled(),
    }
    return normalized


def _normalize_parsed_goal(parsed: dict[str, Any], user_input: str) -> dict[str, Any]:
    parsed = parsed or {}
    parsed_goal = parsed.get("parsed_goal") or {}

    intent = _normalize_intent(parsed_goal.get("intent"), user_input)
    scope = _normalize_scope(parsed_goal.get("scope"), user_input)
    goal_type = _normalize_goal_type(parsed.get("goal_type"), intent, user_input)
    risk_level = _normalize_risk_level(parsed.get("risk_level"), goal_type, user_input)
    target = _normalize_target(parsed_goal.get("target"), user_input)

    fallback_next_action = _default_next_action(goal_type)
    llm_next_action = parsed.get("recommended_next_action") or {}

    summary = _normalize_summary(
        llm_next_action.get("summary"),
        fallback_next_action["summary"],
        target,
    )

    step_type = llm_next_action.get("step_type")
    if step_type not in ALLOWED_STEP_TYPES:
        step_type = fallback_next_action["step_type"]

    steps = _normalize_steps(llm_next_action.get("steps"), fallback_next_action["steps"])

    requires_human_confirmation = llm_next_action.get(
        "requires_human_confirmation",
        fallback_next_action["requires_human_confirmation"],
    )
    requires_human_confirmation = bool(requires_human_confirmation)

    return {
        "raw_input": parsed.get("raw_input") or user_input,
        "parsed_goal": {
            "intent": intent,
            "scope": scope,
            "target": target,
            "source_text": user_input,
            **{
                k: v
                for k, v in parsed_goal.items()
                if k not in {"intent", "scope", "target", "source_text"}
            },
        },
        "goal_type": goal_type,
        "risk_level": risk_level,
        "recommended_next_action": {
            "summary": summary,
            "step_type": step_type,
            "steps": steps,
            "requires_human_confirmation": requires_human_confirmation,
        },
    }


def _parse_goal_with_rules(user_input: str) -> dict[str, Any]:
    text = user_input.lower()

    if any(word in text for word in ["fix", "bug", "error", "issue", "failure"]):
        intent = "fix_issue"
        goal_type = "bug_fix"
        risk_level = "medium"
    elif any(word in text for word in ["understand", "analyze", "inspect", "review", "refactor"]):
        intent = "understand_system"
        goal_type = "system_understanding"
        risk_level = "medium"
    elif any(word in text for word in ["build", "create", "make", "develop"]):
        intent = "build_system"
        goal_type = "system_build"
        risk_level = "low"
    else:
        intent = "general_task"
        goal_type = "general_task"
        risk_level = "low"

    scope = _infer_scope(user_input)

    return {
        "raw_input": user_input,
        "parsed_goal": {
            "intent": intent,
            "scope": scope,
            "target": _infer_target(user_input),
            "source_text": user_input,
        },
        "goal_type": goal_type,
        "risk_level": risk_level,
        "recommended_next_action": _default_next_action(goal_type),
    }


def _normalize_intent(intent: Any, user_input: str) -> str:
    if isinstance(intent, str):
        value = intent.strip().lower()
        if value in {"fix_issue", "bug_fix", "debug_issue"}:
            return "fix_issue"
        if value in {"understand_system", "understand_codebase", "analyze_system", "review_system"}:
            return "understand_system"
        if value in {"build_system", "create_system", "develop_system"}:
            return "build_system"
    return _infer_intent(user_input)


def _normalize_scope(scope: Any, user_input: str) -> str:
    if isinstance(scope, str):
        value = scope.strip().lower()
        if value in ALLOWED_SCOPES:
            return value
        if value in {"fullstack", "full_stack"}:
            return "unspecified"
    return _infer_scope(user_input)


def _normalize_goal_type(goal_type: Any, intent: str, user_input: str) -> str:
    if isinstance(goal_type, str):
        value = goal_type.strip().lower()
        if value in ALLOWED_GOAL_TYPES:
            return value
    if intent == "fix_issue":
        return "bug_fix"
    if intent == "understand_system":
        return "system_understanding"
    if intent == "build_system":
        return "system_build"
    return _infer_goal_type(user_input)


def _normalize_risk_level(risk_level: Any, goal_type: str, user_input: str) -> str:
    if isinstance(risk_level, str):
        value = risk_level.strip().lower()
        if value in ALLOWED_RISK_LEVELS:
            return value
    if goal_type == "bug_fix":
        return "medium"
    if goal_type == "system_understanding" and "legacy" in user_input.lower():
        return "medium"
    return "low"


def _normalize_target(target: Any, user_input: str) -> str:
    if isinstance(target, str) and target.strip():
        value = target.strip()
    else:
        value = _infer_target(user_input)

    if len(value) > 80:
        value = value[:80].rstrip()
    return value


def _normalize_summary(summary: Any, fallback: str, target: str) -> str:
    if not isinstance(summary, str) or not summary.strip():
        summary = fallback
    else:
        summary = " ".join(summary.strip().split())

    if len(summary) > 120:
        summary = summary[:117].rstrip() + "..."

    if summary.lower().startswith("analyze the current system") and target:
        return f"Analyze {target} and prepare an understanding outcome."
    return summary


def _normalize_steps(steps: Any, fallback: list[str]) -> list[str]:
    if not isinstance(steps, list):
        steps = []

    normalized = []
    for item in steps:
        if isinstance(item, str):
            text = " ".join(item.strip().split())
            if text:
                if len(text) > 80:
                    text = text[:77].rstrip() + "..."
                normalized.append(text)

    if not normalized:
        normalized = fallback[:]

    while len(normalized) < 3:
        normalized.append(fallback[min(len(normalized), len(fallback) - 1)])

    return normalized[:3]


def _infer_intent(user_input: str) -> str:
    text = user_input.lower()
    if any(word in text for word in ["fix", "bug", "error", "issue", "failure"]):
        return "fix_issue"
    if any(word in text for word in ["understand", "analyze", "inspect", "review", "refactor"]):
        return "understand_system"
    if any(word in text for word in ["build", "create", "make", "develop"]):
        return "build_system"
    return "general_task"


def _infer_goal_type(user_input: str) -> str:
    text = user_input.lower()
    if any(word in text for word in ["fix", "bug", "error", "issue", "failure"]):
        return "bug_fix"
    if any(word in text for word in ["understand", "analyze", "inspect", "review", "refactor"]):
        return "system_understanding"
    if any(word in text for word in ["build", "create", "make", "develop"]):
        return "system_build"
    return "general_task"


def _infer_scope(user_input: str) -> str:
    text = user_input.lower()
    if any(word in text for word in ["frontend", "dashboard", "ui", "page", "screen"]):
        return "frontend"
    if any(word in text for word in ["backend", "api", "service"]):
        return "backend"
    if any(word in text for word in ["infra", "deploy", "docker", "k8s"]):
        return "infra"
    if any(word in text for word in ["data", "sql", "table", "etl"]):
        return "data"
    return "unspecified"


def _infer_target(user_input: str) -> str:
    text = user_input.strip()
    lowered = text.lower()
    prefixes = [
        "i need to ",
        "please ",
        "help me ",
        "can you ",
        "could you ",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip()
    return text


def _default_next_action(goal_type: str) -> dict[str, Any]:
    if goal_type == "bug_fix":
        return {
            "summary": "Collect issue context and create a repair outcome.",
            "step_type": "collect_context",
            "steps": ["Collect error logs", "Locate affected module", "Prepare repair outcome"],
            "requires_human_confirmation": False,
        }
    if goal_type == "system_understanding":
        return {
            "summary": "Analyze the system and prepare an understanding outcome.",
            "step_type": "analyze_system",
            "steps": ["Collect project assets", "Identify core modules", "Document system behavior"],
            "requires_human_confirmation": False,
        }
    if goal_type == "system_build":
        return {
            "summary": "Define the first build scope and prepare an initial outcome.",
            "step_type": "define_build_scope",
            "steps": ["Clarify scope", "Define MVP boundary", "Prepare first build outcome"],
            "requires_human_confirmation": False,
        }
    return {
        "summary": "Clarify the task and prepare the first actionable outcome.",
        "step_type": "clarify_goal",
        "steps": ["Interpret the request", "Define execution scope", "Prepare first outcome"],
        "requires_human_confirmation": False,
    }


def build_outcome_skeleton(parsed: dict[str, Any]) -> dict[str, Any]:
    goal_type = parsed["goal_type"]
    next_action = parsed["recommended_next_action"]

    if goal_type == "bug_fix":
        current_result = {
            "stage": "goal_captured",
            "summary": "Goal captured. Bug investigation not started yet.",
            "error_context_collected": False,
        }
    elif goal_type == "system_understanding":
        current_result = {
            "stage": "goal_captured",
            "summary": "Goal captured. System analysis not started yet.",
            "analysis_started": False,
        }
    elif goal_type == "system_build":
        current_result = {
            "stage": "goal_captured",
            "summary": "Goal captured. Build workflow not started yet.",
            "delivery_scope_defined": False,
        }
    else:
        current_result = {
            "stage": "goal_captured",
            "summary": "Goal captured. Execution not started yet.",
        }

    return {
        "title": parsed["raw_input"],
        "status": "draft",
        "current_result": current_result,
        "next_action": next_action,
        "risk_boundary": "Local only",
    }
