"""SSE endpoint: stream stage-by-stage progress during autopilot."""
from __future__ import annotations

import asyncio
import json
import threading

from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.routers.project_views import get_project_overview
from app.services.manus_workspace_service import (
    bootstrap_project,
    get_workspace_snapshot,
    run_autopilot,
)

router = APIRouter(prefix="/manus", tags=["manus-events"])

# Lightweight in-memory store for autopilot completion status.
# Key: project_id, Value: {"done": bool, "error": str|None}
_autopilot_status: dict[int, dict] = {}

STAGES = [
    "requirement", "clarification", "prototype",
    "orchestration", "execution", "testing", "delivery",
]


class StreamBootstrapRequest(BaseModel):
    prompt: str
    project_name: str | None = None


@router.post("/projects/bootstrap-stream")
async def bootstrap_stream(payload: StreamBootstrapRequest):
    """Create project + run autopilot, streaming stage completion events via SSE."""

    # Phase 1: Create project synchronously (fast — no LLM call)
    from app.routers.projects import ProjectCreate, create_project
    from app.routers.requirements import RequirementFromInput, create_requirement_from_input, confirm_requirement
    from app.routers.clarifications import ClarificationCreate, create_clarification

    project = create_project(
        ProjectCreate(
            name=(payload.project_name or _make_name(payload.prompt)),
            description=payload.prompt,
            risk_level="medium",
        )
    )
    project_id = project["id"]

    # Create initial requirement + clarification (needed before autopilot)
    requirement = create_requirement_from_input(project_id, RequirementFromInput(user_input=payload.prompt))
    confirm_requirement(requirement["id"])
    create_clarification(
        ClarificationCreate(
            requirement_card_id=requirement["id"],
            questions_json=[],
            answers_json=[],
        )
    )

    # Phase 2: Run autopilot in background thread
    _autopilot_status[project_id] = {"done": False, "error": None}

    def _run():
        try:
            run_autopilot(project_id)
        except Exception as exc:
            _autopilot_status[project_id]["error"] = str(exc)
        finally:
            _autopilot_status[project_id]["done"] = True

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    # Phase 3: Stream SSE events by polling overview
    async def event_generator():
        seen_stages = set()
        prev_stage_key = None

        # Send initial project_created event
        yield {
            "event": "project_created",
            "data": json.dumps({
                "project_id": project_id,
                "name": project["name"],
            }),
        }

        max_polls = 300  # 150 seconds max
        for _ in range(max_polls):
            try:
                overview = get_project_overview(project_id)
            except Exception:
                await asyncio.sleep(0.5)
                continue

            current_stage = overview.get("project", {}).get("current_stage_key")
            stage_objects = overview.get("stage_objects", {})

            # Check for newly completed stages
            for stage_key in STAGES:
                if stage_key in seen_stages:
                    continue
                items = stage_objects.get(
                    _stage_object_key(stage_key), []
                )
                if items:
                    seen_stages.add(stage_key)
                    latest = items[0] if items else {}
                    yield {
                        "event": "stage_update",
                        "data": json.dumps({
                            "stage_key": stage_key,
                            "status": "completed",
                            "content": latest,
                        }),
                    }

            # Check if autopilot is done
            status = _autopilot_status.get(project_id, {})
            if status.get("done"):
                if status.get("error"):
                    yield {
                        "event": "error",
                        "data": json.dumps({"message": status["error"]}),
                    }
                # Send final complete event with full snapshot
                try:
                    snapshot = get_workspace_snapshot(project_id)
                except Exception:
                    snapshot = {"project": {"id": project_id}}
                yield {
                    "event": "complete",
                    "data": json.dumps(snapshot, default=str),
                }
                # Clean up
                _autopilot_status.pop(project_id, None)
                return

            await asyncio.sleep(0.5)

        # Timeout fallback
        yield {
            "event": "error",
            "data": json.dumps({"message": "Autopilot timed out"}),
        }
        _autopilot_status.pop(project_id, None)

    return EventSourceResponse(event_generator())


def _stage_object_key(stage_key: str) -> str:
    """Map stage key to the key used in overview.stage_objects."""
    mapping = {
        "requirement": "requirements",
        "clarification": "clarifications",
        "prototype": "prototypes",
        "orchestration": "orchestration_plans",
        "execution": "execution_runs",
        "testing": "testing_runs",
        "delivery": "deliveries",
    }
    return mapping.get(stage_key, stage_key)


def _make_name(prompt: str) -> str:
    cleaned = (prompt or "").strip()
    if not cleaned:
        return "Untitled Mission"
    for sp in ("。", "\n", ",", "，"):
        cleaned = cleaned.split(sp, 1)[0].strip()
    return cleaned[:24]
