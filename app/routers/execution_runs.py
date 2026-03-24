from fastapi import APIRouter
from pydantic import BaseModel
import psycopg.types.json

from app.db.pool import get_conn
from app.errors import not_found, bad_request
from app.services.stage_executor import advance_stage
from app.services.openclaw_bridge import dispatch as openclaw_dispatch

router = APIRouter(prefix="/execution-runs", tags=["execution-runs"])


class ExecutionRunCreate(BaseModel):
    plan_id: int | None = None
    job_type: str = "backend"
    title: str = "Execute plan step"


@router.post("")
def create_execution_run(payload: ExecutionRunCreate):
    if not payload.plan_id:
        bad_request("plan_id is required")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT project_id FROM orchestration_plans WHERE id = %s",
            (payload.plan_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("orchestration_plan", payload.plan_id)

        project_id = row[0]

        cur.execute(
            """
            INSERT INTO agent_jobs (
                project_id, orchestration_plan_id, job_type, title, payload_json, status, executor_key
            )
            VALUES (%s, %s, %s, %s, '{"source":"phase6_execution","mode":"llm"}'::jsonb, 'pending', 'llm_executor')
            RETURNING id, project_id, orchestration_plan_id, job_type, title, payload_json, status, executor_key, started_at, completed_at, created_at, updated_at
            """,
            (project_id, payload.plan_id, payload.job_type, payload.title),
        )
        created = cur.fetchone()

        advance_stage(project_id, "orchestration", "execution", "execution_run_created", conn=conn)
        conn.commit()
        cur.close()

    return _row_to_run(created)


@router.get("/by-project/{project_id}")
def list_execution_runs_by_project(project_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, orchestration_plan_id, job_type, title, payload_json, status, executor_key, started_at, completed_at, created_at, updated_at
            FROM agent_jobs
            WHERE project_id = %s
            ORDER BY id DESC
            """,
            (project_id,),
        )
        rows = cur.fetchall()
        cur.close()

    return {
        "items": [_row_to_run(r) for r in rows],
        "count": len(rows),
    }


@router.post("/{job_id}/run")
def run_execution(job_id: int):
    """Execute the job using LLM code generation via OpenClaw bridge."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, project_id, orchestration_plan_id FROM agent_jobs WHERE id = %s",
            (job_id,),
        )
        job_row = cur.fetchone()
        if not job_row:
            not_found("execution_run", job_id)

        project_id = job_row[1]
        plan_id = job_row[2]

        # Mark as started
        cur.execute(
            "UPDATE agent_jobs SET status = 'running', started_at = NOW(), updated_at = NOW() WHERE id = %s",
            (job_id,),
        )

        # Get jobs from orchestration plan
        cur.execute(
            "SELECT agent_jobs_json FROM orchestration_plans WHERE id = %s",
            (plan_id,),
        )
        plan_row = cur.fetchone()
        jobs = plan_row[0] if plan_row and plan_row[0] else []

        conn.commit()

        # Execute via OpenClaw bridge (mode from config: llm/shell/mock)
        exec_result = openclaw_dispatch(project_id, jobs) if jobs else {"total_jobs": 0, "completed": 0, "job_results": []}

        # Mark as completed
        cur.execute(
            """
            UPDATE agent_jobs
            SET status = 'completed', completed_at = NOW(), updated_at = NOW(),
                payload_json = payload_json || %s::jsonb
            WHERE id = %s
            RETURNING id, project_id
            """,
            (psycopg.types.json.Json({"execution_result": exec_result}), job_id),
        )

        advance_stage(project_id, "execution", "testing", "execution_run_completed", conn=conn)
        conn.commit()
        cur.close()

    return {
        "ok": True,
        "job_id": job_id,
        "project_id": project_id,
        "current_stage_key": "testing",
        "execution_result": exec_result,
    }


def _row_to_run(r):
    # INSERT RETURNING has 12 cols (includes project_id at index 1)
    # List query has 11 cols (no project_id)
    if len(r) == 12:
        return {
            "id": r[0], "project_id": r[1], "orchestration_plan_id": r[2],
            "job_type": r[3], "title": r[4], "payload_json": r[5], "status": r[6],
            "executor_key": r[7],
            "started_at": r[8].isoformat() if r[8] else None,
            "completed_at": r[9].isoformat() if r[9] else None,
            "created_at": r[10].isoformat() if r[10] else None,
            "updated_at": r[11].isoformat() if r[11] else None,
        }
    return {
        "id": r[0], "orchestration_plan_id": r[1], "job_type": r[2],
        "title": r[3], "payload_json": r[4], "status": r[5],
        "executor_key": r[6],
        "started_at": r[7].isoformat() if r[7] else None,
        "completed_at": r[8].isoformat() if r[8] else None,
        "created_at": r[9].isoformat() if r[9] else None,
        "updated_at": r[10].isoformat() if r[10] else None,
    }
