from __future__ import annotations

from typing import Any


def run_openclaw_verifier(*, executor_result: dict[str, Any], artifact_ref: str) -> dict[str, Any]:
    output_payload = executor_result.get("output_payload", {}) if isinstance(executor_result, dict) else {}
    status = str(output_payload.get("status", executor_result.get("status", "unknown"))).lower()

    passed = status in {"accepted", "completed"}

    checks = [
        {
            "ok": passed,
            "name": "openclaw_task_status",
            "status": status,
            "detail": output_payload,
        }
    ]

    summary = {
        "status": "passed" if passed else "failed",
        "artifact_ref": artifact_ref,
        "executor_status": status,
        "note": "OpenClaw execution accepted/completed."
        if passed
        else "OpenClaw execution failed or errored.",
    }

    return {
        "verifier_name": "openclaw_verify",
        "status": "passed" if passed else "failed",
        "checks": checks,
        "summary": summary,
        "current_result_verification": summary,
        "next_action": {
            "summary": "Review OpenClaw execution trace and decide next browser step."
            if passed
            else "Inspect OpenClaw error and retry with corrected payload.",
            "step_type": "review_browser_execution" if passed else "fix_browser_execution",
            "steps": [
                "Review execution trace files.",
                "Check browser action result.",
                "Decide whether to continue, retry, or escalate.",
            ],
            "requires_human_confirmation": False,
        },
    }
