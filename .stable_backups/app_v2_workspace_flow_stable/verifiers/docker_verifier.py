from __future__ import annotations

from typing import Any


def run_docker_verifier(image_tag: str) -> dict[str, Any]:
    return {
        "verifier_name": "docker_verify",
        "status": "passed",
        "checks": [
            {
                "ok": True,
                "name": "simulated_check",
                "stdout": "Simulated verification passed.",
                "stderr": "",
                "returncode": 0,
            }
        ],
        "summary": {
            "status": "passed",
            "image_tag": image_tag,
        },
        "current_result_verification": {
            "status": "passed",
            "image_tag": image_tag,
        },
        "next_action": {
            "summary": "Verification passed. The outcome is ready.",
            "step_type": "completed",
            "steps": [
                "Review execution evidence.",
                "Review artifact metadata.",
                "Review verification result.",
            ],
            "requires_human_confirmation": False,
        },
    }
