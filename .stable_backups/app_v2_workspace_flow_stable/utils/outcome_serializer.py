import json

def normalize_next_action(value):
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return {"summary": value}
    return {"summary": str(value)}

def serialize_outcome(outcome):
    return {
        "id": outcome.id,
        "goal_id": outcome.goal_id,
        "title": outcome.title,
        "status": outcome.status,
        "current_result": outcome.current_result,
        "next_action": normalize_next_action(outcome.next_action),
        "risk_boundary": outcome.risk_boundary,
        "created_at": outcome.created_at,
        "updated_at": outcome.updated_at,
    }
