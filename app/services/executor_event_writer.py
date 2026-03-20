import json
from app.models.flow_event import FlowEvent

def write_executor_flow_event(db, outcome_id: int, task_name: str, result: dict):
    note_payload = {
        "task_name": task_name,
        "executor_status": result.get("status"),
        "mode": result.get("mode"),
        "returncode": result.get("returncode"),
        "stdout": result.get("stdout"),
        "stderr": result.get("stderr"),
    }

    event = FlowEvent(
        outcome_id=outcome_id,
        from_status=None,
        to_status="executor_called",
        trigger_type="executor_run",
        note=json.dumps(note_payload, ensure_ascii=False),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
