from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.goal import Goal
from app.models.outcome import Outcome
from app.models.flow_event import FlowEvent
from app.services.goal_parser import parse_goal_from_text, build_outcome_skeleton
from app.services.execution_hint_builder import build_execution_hint
from app.services.action_panel_builder import build_action_panel


app = FastAPI(title="AutoFabric API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Request / Response Models
# =========================

class GoalParseRequest(BaseModel):
    user_input: str


class EntrySubmitRequest(BaseModel):
    user_input: str
    source_type: str | None = None
    source_ref: str | None = None
    notes: str | None = None


class ProgressOutcomeRequest(BaseModel):
    status: str = "in_progress"
    stage: str = "next_stage"
    summary: str = "Progress updated."


class ExecutorRunRequest(BaseModel):
    task_name: str
    payload: dict[str, Any]


# =========================
# Utilities
# =========================

def _parse_json_like(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def serialize_goal(goal: Goal) -> dict[str, Any]:
    parsed_goal = goal.parsed_goal or {}
    return {
        "id": goal.id,
        "raw_input": goal.raw_input,
        "parsed_goal": parsed_goal,
        "goal_type": goal.goal_type,
        "risk_level": goal.risk_level,
        "parser_meta": parsed_goal.get("parser_meta"),
        "created_at": goal.created_at,
    }


def serialize_outcome(outcome: Outcome | None) -> dict[str, Any] | None:
    if not outcome:
        return None

    current_result = _parse_json_like(outcome.current_result) or {}
    next_action = _parse_json_like(outcome.next_action) or {}

    return {
        "id": outcome.id,
        "goal_id": outcome.goal_id,
        "title": outcome.title,
        "status": outcome.status,
        "current_result": current_result,
        "next_action": next_action,
        "risk_boundary": outcome.risk_boundary,
        "created_at": outcome.created_at,
        "updated_at": outcome.updated_at,
    }


def serialize_flow_event(event: FlowEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "outcome_id": event.outcome_id,
        "trigger_type": event.trigger_type,
        "to_status": event.to_status,
        "note": event.note,
        "created_at": event.created_at,
    }


def merge_import_context(
    parsed: dict[str, Any],
    source_type: str,
    source_ref: str,
    notes: str | None = None,
) -> dict[str, Any]:
    parsed = parsed.copy()
    parsed_goal = (parsed.get("parsed_goal") or {}).copy()

    parsed_goal["import_context"] = {
        "source_type": source_type,
        "source_ref": source_ref,
        "notes": notes,
    }

    parsed["parsed_goal"] = parsed_goal
    return parsed


def create_goal_and_initial_outcome(parsed: dict[str, Any], db: Session) -> tuple[Goal, Outcome]:
    stored_parsed_goal = {
        **parsed["parsed_goal"],
        "parser_meta": parsed.get("parser_meta"),
    }

    goal = Goal(
        raw_input=parsed["raw_input"],
        parsed_goal=stored_parsed_goal,
        goal_type=parsed["goal_type"],
        risk_level=parsed["risk_level"],
    )
    db.add(goal)
    db.flush()

    skeleton = build_outcome_skeleton(parsed)

    outcome = Outcome(
        goal_id=goal.id,
        title=skeleton["title"],
        status=skeleton["status"],
        current_result=skeleton["current_result"],
        next_action=json.dumps(skeleton["next_action"], ensure_ascii=False),
        risk_boundary=skeleton["risk_boundary"],
    )
    db.add(outcome)
    db.commit()
    db.refresh(goal)
    db.refresh(outcome)

    return goal, outcome


def _build_workspace_response(
    goal: Goal,
    db: Session,
) -> dict[str, Any]:
    outcomes = db.execute(
        select(Outcome).where(Outcome.goal_id == goal.id).order_by(Outcome.id.desc())
    ).scalars().all()

    latest_outcome = outcomes[0] if outcomes else None

    flow_events = db.execute(
        select(FlowEvent)
        .join(Outcome, FlowEvent.outcome_id == Outcome.id)
        .where(Outcome.goal_id == goal.id)
        .order_by(FlowEvent.id.desc())
    ).scalars().all()

    goal_data = serialize_goal(goal)
    latest_outcome_data = serialize_outcome(latest_outcome)
    outcome_list = [serialize_outcome(o) for o in outcomes]
    flow_event_list = [serialize_flow_event(e) for e in flow_events]

    execution_hint = build_execution_hint(goal_data, latest_outcome_data) if latest_outcome_data else None
    recommended_actions = [
        {"label": "启动结果推进", "action_type": "progress_outcome", "target": f"/outcomes/{latest_outcome.id}/progress"}
        if latest_outcome
        else None,
        {"label": "调用 OpenClaw 执行当前步骤", "action_type": "run_executor", "target": "/executors/openclaw/run"}
        if execution_hint
        else None,
        {"label": "查看所有结果对象", "action_type": "view_outcomes", "target": "/outcomes"},
        {"label": "查看所有目标对象", "action_type": "view_goals", "target": "/goals"},
    ]
    recommended_actions = [x for x in recommended_actions if x is not None]

    action_panel = build_action_panel(
        goal=goal_data,
        latest_outcome=latest_outcome_data,
        execution_hint=execution_hint,
        recommended_actions=recommended_actions,
    )

    return {
        "goal": goal_data,
        "latest_outcome": latest_outcome_data,
        "outcomes": outcome_list,
        "flow_events": flow_event_list,
        "execution_hint": execution_hint,
        "recommended_actions": recommended_actions,
        "action_panel": action_panel,
        "summary": {
            "goal_id": goal.id,
            "outcome_count": len(outcome_list),
            "flow_event_count": len(flow_event_list),
            "latest_status": latest_outcome.status if latest_outcome else "unknown",
        },
    }


def _build_workspace_list_item(db: Session, goal: Goal) -> dict[str, Any]:
    latest_outcome = db.execute(
        select(Outcome)
        .where(Outcome.goal_id == goal.id)
        .order_by(Outcome.updated_at.desc(), Outcome.id.desc())
    ).scalars().first()

    serialized_outcome = serialize_outcome(latest_outcome) if latest_outcome else None

    flow_events = db.execute(
        select(FlowEvent)
        .join(Outcome, FlowEvent.outcome_id == Outcome.id)
        .where(Outcome.goal_id == goal.id)
    ).scalars().all()

    goal_data = {
        "id": goal.id,
        "raw_input": goal.raw_input,
        "parsed_goal": goal.parsed_goal,
        "goal_type": goal.goal_type,
        "risk_level": goal.risk_level,
    }

    execution_hint = build_execution_hint(goal_data, serialized_outcome) if serialized_outcome else None

    current_result_raw = latest_outcome.current_result if latest_outcome else {}
    current_result = _parse_json_like(current_result_raw) or {}
    if not isinstance(current_result, dict):
        current_result = {}

    next_action_raw = latest_outcome.next_action if latest_outcome else {}
    next_action = _parse_json_like(next_action_raw) or {}
    if not isinstance(next_action, dict):
        next_action = {}

    return {
        "goal_id": goal.id,
        "title": goal.raw_input,
        "goal_type": goal.goal_type,
        "risk_level": goal.risk_level,
        "scope": (goal.parsed_goal or {}).get("scope"),
        "parser_meta": (goal.parsed_goal or {}).get("parser_meta"),
        "stage": current_result.get("stage"),
        "step_type": next_action.get("step_type"),
        "execution_hint_available": bool(latest_outcome and latest_outcome.status in {"draft", "in_progress"}),
        "executor_touched": bool(current_result.get("last_executor_run")),
        "executor_result_available": bool(current_result.get("last_executor_message")),
        "recommendation_reason_available": bool(execution_hint and execution_hint.get("reason")),
        "flow_event_count": len(flow_events),
        "created_at": goal.created_at,
        "updated_at": latest_outcome.updated_at if latest_outcome else goal.created_at,
        "latest_outcome": serialized_outcome,
    }


def _append_flow_event(
    db: Session,
    outcome_id: int,
    trigger_type: str,
    to_status: str,
    note: str,
) -> FlowEvent:
    event = FlowEvent(
        outcome_id=outcome_id,
        trigger_type=trigger_type,
        to_status=to_status,
        note=note,
    )
    db.add(event)
    db.flush()
    return event


# =========================
# Routes
# =========================

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        row = db.execute(text("select current_database() as database, current_user as user")).mappings().first()
        return {
            "status": "ok",
            "database_connected": True,
            "database_info": {
                "database": row["database"],
                "user": row["user"],
            },
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database_connected": False,
            "database_info": {"error": str(e)},
        }


@app.post("/goals/parse")
def goals_parse(payload: GoalParseRequest):
    parsed = parse_goal_from_text(payload.user_input)
    return {
        "raw_input": parsed["raw_input"],
        "parsed_goal": parsed["parsed_goal"],
        "goal_type": parsed["goal_type"],
        "risk_level": parsed["risk_level"],
        "parser_meta": parsed.get("parser_meta"),
    }


@app.post("/entry/submit")
def entry_submit(payload: EntrySubmitRequest, db: Session = Depends(get_db)):
    parsed = parse_goal_from_text(payload.user_input)

    if payload.source_type and payload.source_ref:
        parsed = merge_import_context(parsed, payload.source_type, payload.source_ref, payload.notes)

    goal, _outcome = create_goal_and_initial_outcome(parsed, db)
    return _build_workspace_response(goal, db)


@app.get("/workspaces")
def list_workspaces(db: Session = Depends(get_db)):
    goals = db.execute(select(Goal).order_by(Goal.id.desc())).scalars().all()
    items = [_build_workspace_list_item(db, goal) for goal in goals]
    items.sort(key=lambda x: x["updated_at"] or x["created_at"], reverse=True)
    return {"items": items}


@app.get("/workspaces/{goal_id}")
def get_workspace(goal_id: int, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return _build_workspace_response(goal, db)


@app.get("/goals")
def list_goals(db: Session = Depends(get_db)):
    rows = db.execute(select(Goal).order_by(Goal.id.desc())).scalars().all()
    return {"items": [serialize_goal(row) for row in rows]}


@app.get("/goals/list-view")
def list_goals_view(db: Session = Depends(get_db)):
    rows = db.execute(select(Goal).order_by(Goal.id.desc())).scalars().all()
    items = [
        {
            "id": row.id,
            "raw_input": row.raw_input,
            "goal_type": row.goal_type,
            "risk_level": row.risk_level,
            "parser_meta": (row.parsed_goal or {}).get("parser_meta"),
            "created_at": row.created_at,
        }
        for row in rows
    ]
    return {"items": items}


@app.get("/outcomes")
def list_outcomes(db: Session = Depends(get_db)):
    rows = db.execute(select(Outcome).order_by(Outcome.id.desc())).scalars().all()
    items = []
    for row in rows:
        serialized = serialize_outcome(row)
        items.append(
            {
                "id": serialized["id"],
                "goal_id": serialized["goal_id"],
                "title": serialized["title"],
                "status": serialized["status"],
                "stage": (serialized["current_result"] or {}).get("stage"),
                "summary": (serialized["current_result"] or {}).get("summary"),
                "updated_at": serialized["updated_at"],
            }
        )
    return {"items": items}


@app.post("/outcomes/{outcome_id}/progress")
def progress_outcome(
    outcome_id: int,
    payload: ProgressOutcomeRequest,
    db: Session = Depends(get_db),
):
    outcome = db.get(Outcome, outcome_id)
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    current_result = _parse_json_like(outcome.current_result) or {}
    current_result["stage"] = payload.stage
    current_result["summary"] = payload.summary

    outcome.status = payload.status
    outcome.current_result = current_result
    outcome.updated_at = datetime.utcnow()

    _append_flow_event(
        db=db,
        outcome_id=outcome.id,
        trigger_type="progress_outcome",
        to_status=payload.status,
        note=payload.summary,
    )

    db.commit()
    db.refresh(outcome)

    goal = db.get(Goal, outcome.goal_id)
    return _build_workspace_response(goal, db)


@app.post("/executors/openclaw/run")
def run_openclaw_executor(payload: ExecutorRunRequest, db: Session = Depends(get_db)):
    payload_data = payload.payload or {}
    outcome_id = payload_data.get("outcome_id")
    if not outcome_id:
        raise HTTPException(status_code=400, detail="payload.outcome_id is required")

    outcome = db.get(Outcome, outcome_id)
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    current_result = _parse_json_like(outcome.current_result) or {}

    executor_run = {
        "task_name": payload.task_name,
        "mode": "bridge",
        "status": "success",
        "executed_at": datetime.utcnow().isoformat(),
        "payload": payload_data,
    }

    message = f"OpenClaw bridge executed: {payload.task_name}"

    current_result["last_executor_run"] = executor_run
    current_result["last_executor_message"] = message

    if outcome.status == "draft":
        outcome.status = "in_progress"

    outcome.current_result = current_result
    outcome.updated_at = datetime.utcnow()

    _append_flow_event(
        db=db,
        outcome_id=outcome.id,
        trigger_type="run_executor",
        to_status=outcome.status,
        note=message,
    )

    db.commit()
    db.refresh(outcome)

    goal = db.get(Goal, outcome.goal_id)
    return _build_workspace_response(goal, db)