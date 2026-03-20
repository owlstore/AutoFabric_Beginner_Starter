from typing import Any

def normalize_action_payload(action_type: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = payload or {}

    if action_type == "progress_outcome":
        return {
            "status": payload.get("status", "in_progress"),
            "stage": payload.get("stage", "next_stage"),
            "summary": payload.get("summary", "Progress updated from action panel."),
            "next_action": payload.get("next_action"),
        }

    if action_type == "run_executor":
        return payload

    return payload
