from copy import deepcopy
from typing import Any


def merge_import_context(
    parsed: dict[str, Any],
    source_type: str | None = None,
    source_ref: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    result = deepcopy(parsed or {})

    raw_input = result.get("raw_input", "")
    parsed_goal = result.get("parsed_goal")
    if not isinstance(parsed_goal, dict):
        parsed_goal = {}

    parsed_goal.setdefault("source_text", raw_input)

    source_context: dict[str, Any] = {}

    if notes:
        source_context["notes"] = notes
    if source_ref:
        source_context["source_ref"] = source_ref
    if source_type:
        source_context["source_type"] = source_type

    if source_context:
        parsed_goal["source_context"] = source_context

    result["parsed_goal"] = parsed_goal
    return result
