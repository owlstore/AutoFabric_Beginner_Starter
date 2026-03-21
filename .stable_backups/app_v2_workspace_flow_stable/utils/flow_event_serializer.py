def serialize_flow_event(event):
    return {
        "id": event.id,
        "outcome_id": event.outcome_id,
        "from_status": event.from_status,
        "to_status": event.to_status,
        "trigger_type": event.trigger_type,
        "note": event.note,
        "created_at": event.created_at,
    }
