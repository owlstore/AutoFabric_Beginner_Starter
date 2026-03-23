from fastapi import APIRouter
from pydantic import BaseModel
import psycopg.types.json

from app.db.pool import get_conn
from app.errors import not_found, bad_request
from app.services.stage_executor import advance_stage
from app.stages.testing import generate_tests, review_code, write_test_files, run_tests_in_sandbox

router = APIRouter(prefix="/testing-runs", tags=["testing-runs"])


class TestingRunCreate(BaseModel):
    job_id: int | None = None
    title: str = "Run verification"
    note: str | None = None


@router.post("")
def create_testing_run(payload: TestingRunCreate):
    if not payload.job_id:
        bad_request("job_id is required")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT project_id FROM agent_jobs WHERE id = %s",
            (payload.job_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("execution_run", payload.job_id)

        project_id = row[0]

        cur.execute(
            """
            INSERT INTO testing_runs (
                project_id, execution_run_id, title, note, status, result_json
            )
            VALUES (%s, %s, %s, %s, 'pending', '{}'::jsonb)
            RETURNING id, project_id, execution_run_id, title, note, status, result_json, created_at, updated_at
            """,
            (project_id, payload.job_id, payload.title, payload.note),
        )
        created = cur.fetchone()

        advance_stage(project_id, "execution", "testing", "testing_run_created", conn=conn)
        conn.commit()
        cur.close()

    return _row_to_test(created)


@router.get("/by-project/{project_id}")
def list_testing_runs_by_project(project_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, project_id, execution_run_id, title, note, status, result_json, created_at, updated_at
            FROM testing_runs
            WHERE project_id = %s
            ORDER BY id DESC
            """,
            (project_id,),
        )
        rows = cur.fetchall()
        cur.close()

    return {
        "items": [_row_to_test(r) for r in rows],
        "count": len(rows),
    }


@router.post("/{testing_run_id}/execute")
def execute_testing(testing_run_id: int):
    """Generate tests with LLM, run in Docker sandbox, and do code review."""
    from pathlib import Path
    from app.config import config as app_config

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, project_id FROM testing_runs WHERE id = %s",
            (testing_run_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("testing_run", testing_run_id)

        project_id = row[1]

        # Mark as running
        cur.execute(
            "UPDATE testing_runs SET status = 'running', updated_at = NOW() WHERE id = %s",
            (testing_run_id,),
        )
        conn.commit()

        # Gather generated source files
        src_dir = Path(app_config.openclaw.output_dir) / f"project_{project_id}" / "src"
        source_files = []
        if src_dir.exists():
            for p in src_dir.rglob("*"):
                if p.is_file() and p.suffix in (".py", ".js", ".jsx", ".ts", ".tsx"):
                    try:
                        source_files.append({"path": str(p.relative_to(src_dir)), "content": p.read_text()})
                    except Exception:
                        pass

        # Get requirement card for context
        cur.execute(
            "SELECT title, summary FROM requirement_cards WHERE project_id = %s ORDER BY id DESC LIMIT 1",
            (project_id,),
        )
        req = cur.fetchone()
        req_card = {"title": req[0] or "", "summary": req[1] or ""} if req else {}

        # Step 1: LLM generates tests
        test_data = generate_tests(source_files, req_card) if source_files else {"test_files": [], "test_config": {}}
        written = write_test_files(project_id, test_data)

        # Step 2: LLM code review
        review = review_code(source_files) if source_files else {"issues": [], "overall_score": 0, "summary": "No source files to review"}

        # Step 3: Docker sandbox (optional)
        sandbox_result = run_tests_in_sandbox(project_id, test_data.get("test_config", {}).get("framework", "pytest"))

        result_json = {
            "tests_generated": len(test_data.get("test_files", [])),
            "test_files_written": written,
            "code_review": review,
            "sandbox_result": sandbox_result,
            "passed": sandbox_result.get("passed", None),
        }

        status = "passed" if sandbox_result.get("passed") else "failed"
        if sandbox_result.get("passed") is None:
            status = "review_only"

        cur.execute(
            """
            UPDATE testing_runs
            SET status = %s, result_json = %s::jsonb, updated_at = NOW()
            WHERE id = %s
            """,
            (status, psycopg.types.json.Json(result_json), testing_run_id),
        )
        conn.commit()
        cur.close()

    return {
        "ok": True,
        "testing_run_id": testing_run_id,
        "project_id": project_id,
        "status": status,
        "result": result_json,
    }


@router.post("/{testing_run_id}/pass")
def pass_testing_run(testing_run_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE testing_runs
            SET status = 'passed', result_json = result_json || '{"manual_pass": true}'::jsonb, updated_at = NOW()
            WHERE id = %s
            RETURNING id, project_id
            """,
            (testing_run_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("testing_run", testing_run_id)

        project_id = row[1]
        advance_stage(project_id, "testing", "delivery", "testing_passed", conn=conn)
        conn.commit()
        cur.close()

    return {
        "ok": True,
        "testing_run_id": testing_run_id,
        "project_id": project_id,
        "current_stage_key": "delivery",
    }


def _row_to_test(r):
    return {
        "id": r[0], "project_id": r[1], "execution_run_id": r[2],
        "title": r[3], "note": r[4], "status": r[5], "result_json": r[6],
        "created_at": r[7].isoformat() if r[7] else None,
        "updated_at": r[8].isoformat() if r[8] else None,
    }
