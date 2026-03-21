from __future__ import annotations

from typing import Any


def run_build_executor(goal_text: str, outcome_id: int) -> dict[str, Any]:
    image_tag = f"autofabric-outcome-{outcome_id}:latest"
    artifact_dir = f".autofabric_runs/outcome_{outcome_id}"

    return {
        "executor_name": "docker_worker",
        "task_name": "docker_build_environment",
        "status": "completed",
        "input_payload": {
            "target": goal_text,
            "image_tag": image_tag,
        },
        "output_payload": {
            "returncode": 0,
            "artifact_dir": artifact_dir,
            "message": "Simulated execution completed.",
        },
        "artifact": {
            "artifact_type": "docker_image",
            "file_path": artifact_dir,
            "artifact_ref": image_tag,
            "artifact_metadata": {
                "image_tag": image_tag,
                "artifact_dir": artifact_dir,
            },
        },
        "current_result": {
            "stage": "verification_completed",
            "summary": "Execution and verification completed.",
            "artifact": {
                "type": "docker_image",
                "image_tag": image_tag,
                "artifact_dir": artifact_dir,
            },
        },
    }
