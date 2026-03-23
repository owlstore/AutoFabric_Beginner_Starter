from fastapi import APIRouter
from pydantic import BaseModel

from app.db.pool import get_conn
from app.errors import not_found, bad_request
from app.services.stage_executor import advance_stage
from app.stages.requirement import analyze_requirement as llm_analyze

router = APIRouter(tags=["requirements"])


class RequirementCreate(BaseModel):
    title: str
    summary: str | None = None
    target_users: str | None = None
    problem_statement: str | None = None


class RequirementFromInput(BaseModel):
    user_input: str


@router.post("/projects/{project_id}/requirements")
def create_requirement(project_id: int, payload: RequirementCreate):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM projects WHERE id = %s", (project_id,))
        if not cur.fetchone():
            not_found("project", project_id)

        cur.execute(
            "SELECT COALESCE(MAX(version_no), 0) + 1 FROM requirement_cards WHERE project_id = %s",
            (project_id,),
        )
        version_no = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO requirement_cards (
                project_id, version_no, title, summary, target_users, problem_statement, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'draft')
            RETURNING id, version_no, title, summary, target_users, problem_statement, status, created_at, updated_at
        """, (project_id, version_no, payload.title, payload.summary, payload.target_users, payload.problem_statement))
        row = cur.fetchone()

        advance_stage(project_id, None, "requirement", "requirement_created", conn=conn)
        conn.commit()
        cur.close()

    return {
        "id": row[0], "project_id": project_id, "version_no": row[1],
        "title": row[2], "summary": row[3], "target_users": row[4],
        "problem_statement": row[5], "status": row[6],
        "created_at": row[7].isoformat() if row[7] else None,
        "updated_at": row[8].isoformat() if row[8] else None,
    }


@router.post("/projects/{project_id}/requirements/from-input")
def create_requirement_from_input(project_id: int, payload: RequirementFromInput):
    """Use LLM to analyze user input and create a structured requirement card."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM projects WHERE id = %s", (project_id,))
        if not cur.fetchone():
            not_found("project", project_id)

        # Call LLM to analyze requirement
        card = llm_analyze(payload.user_input)

        cur.execute(
            "SELECT COALESCE(MAX(version_no), 0) + 1 FROM requirement_cards WHERE project_id = %s",
            (project_id,),
        )
        version_no = cur.fetchone()[0]

        import psycopg.types.json
        cur.execute("""
            INSERT INTO requirement_cards (
                project_id, version_no, title, summary, target_users, problem_statement, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'draft')
            RETURNING id, version_no, title, summary, target_users, problem_statement, status, created_at, updated_at
        """, (
            project_id, version_no,
            card.get("title", "Untitled"),
            card.get("summary", ""),
            card.get("target_users", ""),
            card.get("problem_statement", ""),
        ))
        row = cur.fetchone()

        advance_stage(project_id, None, "requirement", "requirement_created_by_llm", conn=conn)
        conn.commit()
        cur.close()

    return {
        "id": row[0], "project_id": project_id, "version_no": row[1],
        "title": row[2], "summary": row[3], "target_users": row[4],
        "problem_statement": row[5], "status": row[6],
        "created_at": row[7].isoformat() if row[7] else None,
        "updated_at": row[8].isoformat() if row[8] else None,
        "llm_analysis": card,
    }


@router.get("/requirements/{requirement_id}")
def get_requirement(requirement_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, project_id, version_no, title, summary, target_users, problem_statement, status, confirmed_at, created_at, updated_at
            FROM requirement_cards
            WHERE id = %s
        """, (requirement_id,))
        row = cur.fetchone()
        cur.close()

    if not row:
        not_found("requirement", requirement_id)

    return {
        "id": row[0], "project_id": row[1], "version_no": row[2],
        "title": row[3], "summary": row[4], "target_users": row[5],
        "problem_statement": row[6], "status": row[7],
        "confirmed_at": row[8].isoformat() if row[8] else None,
        "created_at": row[9].isoformat() if row[9] else None,
        "updated_at": row[10].isoformat() if row[10] else None,
    }


@router.post("/requirements/{requirement_id}/analyze")
def analyze_requirement_endpoint(requirement_id: int):
    """Use LLM to analyze a requirement card for completeness."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, summary, target_users, problem_statement
            FROM requirement_cards
            WHERE id = %s
        """, (requirement_id,))
        row = cur.fetchone()
        cur.close()

    if not row:
        not_found("requirement", requirement_id)

    # Build requirement text for LLM analysis
    req_text = f"Title: {row[1] or ''}\nSummary: {row[2] or ''}\nTarget Users: {row[3] or ''}\nProblem: {row[4] or ''}"
    card = llm_analyze(req_text)

    missing = []
    if not row[1]:
        missing.append("title")
    if not row[2]:
        missing.append("summary")
    if not row[3]:
        missing.append("target_users")
    if not row[4]:
        missing.append("problem_statement")

    return {
        "requirement_id": requirement_id,
        "ready_for_clarification_or_confirm": len(missing) == 0,
        "missing_fields": missing,
        "suggested_next_stage": "clarification" if missing else "prototype",
        "llm_analysis": card,
    }


@router.post("/requirements/{requirement_id}/confirm")
def confirm_requirement(requirement_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE requirement_cards
            SET status = 'confirmed', confirmed_at = NOW(), updated_at = NOW()
            WHERE id = %s
            RETURNING id, project_id
        """, (requirement_id,))
        row = cur.fetchone()
        if not row:
            not_found("requirement", requirement_id)

        project_id = row[1]
        advance_stage(
            project_id, "requirement", "clarification", "requirement_confirmed",
            conn=conn,
            approval={
                "approval_type": "requirement_confirm",
                "target_ref_type": "requirement_card",
                "target_ref_id": requirement_id,
                "note": "Requirement confirmed",
            },
        )
        conn.commit()
        cur.close()

    return {
        "ok": True,
        "requirement_id": requirement_id,
        "project_id": project_id,
        "current_stage_key": "clarification",
    }
