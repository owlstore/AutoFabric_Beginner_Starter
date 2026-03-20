import json

def build_synced_current_result(existing_current_result: dict | None, result: dict) -> dict:
    current = dict(existing_current_result or {})

    message = None
    stdout = result.get("stdout")
    if stdout:
        try:
            parsed = json.loads(stdout)
            message = parsed.get("message")
        except Exception:
            message = stdout

    current["last_executor_run"] = {
        "task_name": result.get("task_name"),
        "status": result.get("status"),
        "mode": result.get("mode"),
        "returncode": result.get("returncode"),
        "executed_at": result.get("executed_at"),
    }

    if message:
        current["last_executor_message"] = message

    return current
