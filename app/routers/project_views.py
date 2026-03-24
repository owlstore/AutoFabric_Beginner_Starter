from fastapi import APIRouter

from app.db.pool import get_conn
from app.errors import not_found

router = APIRouter(prefix="/project-views", tags=["project-views"])


def _iso(val):
    return val.isoformat() if val else None


@router.get("/{project_id}/overview")
def get_project_overview(project_id: int):
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, description, current_stage_key, status, risk_level, created_at, updated_at
            FROM projects WHERE id = %s
        """, (project_id,))
        p = cur.fetchone()
        if not p:
            not_found("project", project_id)

        cur.execute("""
            SELECT stage_key, stage_status, is_current, entered_at, exited_at, updated_at
            FROM project_stage_states WHERE project_id = %s
            ORDER BY entered_at ASC NULLS LAST, stage_key ASC
        """, (project_id,))
        stage_rows = cur.fetchall()

        # Counts
        counts = {}
        for table, key in [
            ("requirement_cards", "requirements"),
            ("clarification_rounds", "clarifications"),
            ("prototype_specs", "prototypes"),
            ("orchestration_plans", "orchestration_plans"),
            ("agent_jobs", "execution_runs"),
            ("testing_runs", "testing_runs"),
            ("delivery_packages", "deliveries"),
        ]:
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id = %s", (project_id,))
            counts[key] = cur.fetchone()[0]

        # Transitions
        cur.execute("""
            SELECT id, from_stage_key, to_stage_key, transition_reason, triggered_by, created_at
            FROM stage_transitions WHERE project_id = %s ORDER BY id ASC
        """, (project_id,))
        transition_rows = cur.fetchall()

        # Latest objects
        latest = {}

        cur.execute("SELECT id, title, status, created_at, updated_at FROM requirement_cards WHERE project_id = %s ORDER BY id DESC LIMIT 1", (project_id,))
        r = cur.fetchone()
        latest["requirement"] = {"id": r[0], "title": r[1], "status": r[2], "created_at": _iso(r[3]), "updated_at": _iso(r[4])} if r else None

        cur.execute("SELECT id, round_no, status, created_at, updated_at FROM clarification_rounds WHERE project_id = %s ORDER BY id DESC LIMIT 1", (project_id,))
        r = cur.fetchone()
        latest["clarification"] = {"id": r[0], "round_no": r[1], "status": r[2], "created_at": _iso(r[3]), "updated_at": _iso(r[4])} if r else None

        cur.execute("SELECT id, version_no, status, figma_url, created_at, updated_at FROM prototype_specs WHERE project_id = %s ORDER BY id DESC LIMIT 1", (project_id,))
        r = cur.fetchone()
        latest["prototype"] = {"id": r[0], "version_no": r[1], "status": r[2], "figma_url": r[3], "created_at": _iso(r[4]), "updated_at": _iso(r[5])} if r else None

        cur.execute("SELECT id, version_no, status, created_at, updated_at FROM orchestration_plans WHERE project_id = %s ORDER BY id DESC LIMIT 1", (project_id,))
        r = cur.fetchone()
        latest["orchestration"] = {"id": r[0], "version_no": r[1], "status": r[2], "created_at": _iso(r[3]), "updated_at": _iso(r[4])} if r else None

        cur.execute("SELECT id, title, status, executor_key, started_at, completed_at, created_at, updated_at FROM agent_jobs WHERE project_id = %s ORDER BY id DESC LIMIT 1", (project_id,))
        r = cur.fetchone()
        latest["execution"] = {"id": r[0], "title": r[1], "status": r[2], "executor_key": r[3], "started_at": _iso(r[4]), "completed_at": _iso(r[5]), "created_at": _iso(r[6]), "updated_at": _iso(r[7])} if r else None

        cur.execute("SELECT id, title, status, note, created_at, updated_at FROM testing_runs WHERE project_id = %s ORDER BY id DESC LIMIT 1", (project_id,))
        r = cur.fetchone()
        latest["testing"] = {"id": r[0], "title": r[1], "status": r[2], "note": r[3], "created_at": _iso(r[4]), "updated_at": _iso(r[5])} if r else None

        cur.execute("SELECT id, status, published_at, created_at, updated_at FROM delivery_packages WHERE project_id = %s ORDER BY id DESC LIMIT 1", (project_id,))
        r = cur.fetchone()
        latest["delivery"] = {"id": r[0], "status": r[1], "published_at": _iso(r[2]), "created_at": _iso(r[3]), "updated_at": _iso(r[4])} if r else None

        # Full object lists
        stage_objects = {}

        cur.execute("SELECT id, version_no, title, summary, target_users, problem_statement, status, confirmed_at, created_at, updated_at FROM requirement_cards WHERE project_id = %s ORDER BY id DESC", (project_id,))
        stage_objects["requirements"] = [
            {"id": r[0], "version_no": r[1], "title": r[2], "summary": r[3], "target_users": r[4], "problem_statement": r[5], "status": r[6], "confirmed_at": _iso(r[7]), "created_at": _iso(r[8]), "updated_at": _iso(r[9])}
            for r in cur.fetchall()
        ]

        cur.execute("SELECT id, requirement_card_id, round_no, questions_json, answers_json, resolved_json, status, created_at, updated_at FROM clarification_rounds WHERE project_id = %s ORDER BY round_no ASC", (project_id,))
        stage_objects["clarifications"] = [
            {"id": r[0], "requirement_card_id": r[1], "round_no": r[2], "questions_json": r[3], "answers_json": r[4], "resolved_json": r[5], "status": r[6], "created_at": _iso(r[7]), "updated_at": _iso(r[8])}
            for r in cur.fetchall()
        ]

        cur.execute("SELECT id, requirement_card_id, version_no, ia_json, page_flow_json, module_map_json, api_draft_json, figma_url, status, confirmed_at, created_at, updated_at FROM prototype_specs WHERE project_id = %s ORDER BY version_no DESC", (project_id,))
        stage_objects["prototypes"] = [
            {"id": r[0], "requirement_card_id": r[1], "version_no": r[2], "ia_json": r[3], "page_flow_json": r[4], "module_map_json": r[5], "api_draft_json": r[6], "figma_url": r[7], "status": r[8], "confirmed_at": _iso(r[9]), "created_at": _iso(r[10]), "updated_at": _iso(r[11])}
            for r in cur.fetchall()
        ]

        cur.execute("SELECT id, prototype_spec_id, version_no, epic_json, feature_json, tasks_json, agent_jobs_json, acceptance_criteria_json, dependency_graph_json, status, created_at, updated_at FROM orchestration_plans WHERE project_id = %s ORDER BY version_no DESC", (project_id,))
        stage_objects["orchestration_plans"] = [
            {"id": r[0], "prototype_spec_id": r[1], "version_no": r[2], "epic_json": r[3], "feature_json": r[4], "tasks_json": r[5], "agent_jobs_json": r[6], "acceptance_criteria_json": r[7], "dependency_graph_json": r[8], "status": r[9], "created_at": _iso(r[10]), "updated_at": _iso(r[11])}
            for r in cur.fetchall()
        ]

        cur.execute("SELECT id, orchestration_plan_id, job_type, title, payload_json, status, executor_key, started_at, completed_at, created_at, updated_at FROM agent_jobs WHERE project_id = %s ORDER BY id DESC", (project_id,))
        stage_objects["execution_runs"] = [
            {"id": r[0], "orchestration_plan_id": r[1], "job_type": r[2], "title": r[3], "payload_json": r[4], "status": r[5], "executor_key": r[6], "started_at": _iso(r[7]), "completed_at": _iso(r[8]), "created_at": _iso(r[9]), "updated_at": _iso(r[10])}
            for r in cur.fetchall()
        ]

        cur.execute("SELECT id, execution_run_id, title, note, status, result_json, created_at, updated_at FROM testing_runs WHERE project_id = %s ORDER BY id DESC", (project_id,))
        stage_objects["testing_runs"] = [
            {"id": r[0], "execution_run_id": r[1], "title": r[2], "note": r[3], "status": r[4], "result_json": r[5], "created_at": _iso(r[6]), "updated_at": _iso(r[7])}
            for r in cur.fetchall()
        ]

        cur.execute("SELECT id, summary_md, prototype_refs_json, engineering_refs_json, testing_refs_json, process_refs_json, next_step_json, published_at, status, created_at, updated_at FROM delivery_packages WHERE project_id = %s ORDER BY id DESC", (project_id,))
        stage_objects["deliveries"] = [
            {"id": r[0], "summary_md": r[1], "prototype_refs_json": r[2], "engineering_refs_json": r[3], "testing_refs_json": r[4], "process_refs_json": r[5], "next_step_json": r[6], "published_at": _iso(r[7]), "status": r[8], "created_at": _iso(r[9]), "updated_at": _iso(r[10])}
            for r in cur.fetchall()
        ]

        cur.close()

    return {
        "project": {
            "id": p[0], "name": p[1], "description": p[2],
            "current_stage_key": p[3], "status": p[4], "risk_level": p[5],
            "created_at": _iso(p[6]), "updated_at": _iso(p[7]),
        },
        "counts": counts,
        "stages": [
            {"stage_key": r[0], "stage_status": r[1], "is_current": r[2], "entered_at": _iso(r[3]), "exited_at": _iso(r[4]), "updated_at": _iso(r[5])}
            for r in stage_rows
        ],
        "transitions": [
            {"id": r[0], "from_stage_key": r[1], "to_stage_key": r[2], "transition_reason": r[3], "triggered_by": r[4], "created_at": _iso(r[5])}
            for r in transition_rows
        ],
        "latest_objects": latest,
        "stage_objects": stage_objects,
    }
