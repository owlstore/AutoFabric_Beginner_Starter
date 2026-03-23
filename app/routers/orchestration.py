from fastapi import APIRouter
from pydantic import BaseModel
import psycopg.types.json

from app.db.pool import get_conn
from app.errors import not_found, bad_request
from app.services.stage_executor import advance_stage
from app.stages.orchestration import plan_orchestration, to_openclaw_jobs

router = APIRouter(prefix="/orchestration-plans", tags=["orchestration"])


class OrchestrationPlanCreate(BaseModel):
    prototype_spec_id: int | None = None


@router.post("")
def create_orchestration_plan(payload: OrchestrationPlanCreate):
    if not payload.prototype_spec_id:
        bad_request("prototype_spec_id is required")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT project_id FROM prototype_specs WHERE id = %s",
            (payload.prototype_spec_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("prototype_spec", payload.prototype_spec_id)

        project_id = row[0]

        cur.execute(
            "SELECT COALESCE(MAX(version_no), 0) + 1 FROM orchestration_plans WHERE project_id = %s",
            (project_id,),
        )
        version_no = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO orchestration_plans (
                project_id, prototype_spec_id, version_no,
                epic_json, feature_json, tasks_json, agent_jobs_json,
                acceptance_criteria_json, dependency_graph_json, status
            )
            VALUES (%s, %s, %s, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, '{}'::jsonb, 'draft')
            RETURNING id, project_id, prototype_spec_id, version_no, epic_json, feature_json, tasks_json, agent_jobs_json, acceptance_criteria_json, dependency_graph_json, status, created_at, updated_at
            """,
            (project_id, payload.prototype_spec_id, version_no),
        )
        created = cur.fetchone()

        advance_stage(project_id, "prototype", "orchestration", "orchestration_created", conn=conn)
        conn.commit()
        cur.close()

    return _row_to_plan(created)


@router.get("/by-project/{project_id}")
def list_orchestration_plans_by_project(project_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, prototype_spec_id, version_no, epic_json, feature_json, tasks_json, agent_jobs_json, acceptance_criteria_json, dependency_graph_json, status, created_at, updated_at
            FROM orchestration_plans
            WHERE project_id = %s
            ORDER BY version_no DESC, id DESC
            """,
            (project_id,),
        )
        rows = cur.fetchall()
        cur.close()

    return {
        "items": [_row_to_plan(r) for r in rows],
        "count": len(rows),
    }


@router.post("/{plan_id}/generate")
def generate_orchestration(plan_id: int):
    """Use LLM to generate a full orchestration plan."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, project_id, prototype_spec_id FROM orchestration_plans WHERE id = %s",
            (plan_id,),
        )
        plan_row = cur.fetchone()
        if not plan_row:
            not_found("orchestration_plan", plan_id)

        project_id = plan_row[1]
        proto_id = plan_row[2]

        # Gather context for LLM
        cur.execute(
            "SELECT title, summary, target_users, problem_statement FROM requirement_cards WHERE project_id = %s ORDER BY id DESC LIMIT 1",
            (project_id,),
        )
        req = cur.fetchone()
        req_card = {"title": req[0] or "", "summary": req[1] or "", "target_users": req[2] or "", "problem_statement": req[3] or ""} if req else {}

        ia, modules = None, None
        if proto_id:
            cur.execute("SELECT ia_json, module_map_json FROM prototype_specs WHERE id = %s", (proto_id,))
            proto = cur.fetchone()
            if proto:
                ia = proto[0]
                modules = proto[1]

        # Call LLM
        plan = plan_orchestration(req_card, ia=ia, modules=modules)
        jobs = to_openclaw_jobs(plan)

        cur.execute(
            """
            UPDATE orchestration_plans
            SET
                epic_json = %s::jsonb,
                feature_json = %s::jsonb,
                tasks_json = %s::jsonb,
                agent_jobs_json = %s::jsonb,
                dependency_graph_json = %s::jsonb,
                updated_at = NOW()
            WHERE id = %s
            RETURNING id, project_id, prototype_spec_id, version_no, epic_json, feature_json, tasks_json, agent_jobs_json, acceptance_criteria_json, dependency_graph_json, status, created_at, updated_at
            """,
            (
                psycopg.types.json.Json(plan.get("epic", "")),
                psycopg.types.json.Json(plan.get("features", [])),
                psycopg.types.json.Json(plan.get("execution_order", [])),
                psycopg.types.json.Json(jobs),
                psycopg.types.json.Json({"risk_notes": plan.get("risk_notes", [])}),
                plan_id,
            ),
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()

    return _row_to_plan(row)


@router.post("/{plan_id}/approve")
def approve_orchestration_plan(plan_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE orchestration_plans
            SET status = 'approved', updated_at = NOW()
            WHERE id = %s
            RETURNING id, project_id, status
            """,
            (plan_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("orchestration_plan", plan_id)

        project_id = row[1]
        advance_stage(project_id, "orchestration", "execution", "orchestration_approved", conn=conn)
        conn.commit()
        cur.close()

    return {
        "ok": True,
        "plan_id": plan_id,
        "project_id": project_id,
        "current_stage_key": "execution",
    }


def _row_to_plan(r):
    # RETURNING from create/update has 13 cols (includes project_id at index 1)
    # List query has 12 cols (no project_id)
    if len(r) == 13:
        return {
            "id": r[0], "project_id": r[1], "prototype_spec_id": r[2], "version_no": r[3],
            "epic_json": r[4], "feature_json": r[5], "tasks_json": r[6],
            "agent_jobs_json": r[7], "acceptance_criteria_json": r[8],
            "dependency_graph_json": r[9], "status": r[10],
            "created_at": r[11].isoformat() if r[11] else None,
            "updated_at": r[12].isoformat() if r[12] else None,
        }
    return {
        "id": r[0], "prototype_spec_id": r[1], "version_no": r[2],
        "epic_json": r[3], "feature_json": r[4], "tasks_json": r[5],
        "agent_jobs_json": r[6], "acceptance_criteria_json": r[7],
        "dependency_graph_json": r[8], "status": r[9],
        "created_at": r[10].isoformat() if r[10] else None,
        "updated_at": r[11].isoformat() if r[11] else None,
    }
