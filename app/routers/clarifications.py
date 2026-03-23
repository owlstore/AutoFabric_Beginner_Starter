from fastapi import APIRouter
from pydantic import BaseModel
import psycopg.types.json

from app.db.pool import get_conn
from app.errors import not_found, bad_request
from app.services.stage_executor import advance_stage
from app.stages.clarification import generate_questions, refine_requirement

router = APIRouter(prefix="/clarifications", tags=["clarifications"])


class ClarificationCreate(BaseModel):
    requirement_card_id: int | None = None
    questions_json: list = []
    answers_json: list = []


class ClarificationReply(BaseModel):
    answers_json: list


@router.post("")
def create_clarification(payload: ClarificationCreate):
    if not payload.requirement_card_id:
        bad_request("requirement_card_id is required")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT project_id FROM requirement_cards WHERE id = %s",
            (payload.requirement_card_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("requirement_card", payload.requirement_card_id)

        project_id = row[0]

        # If no questions provided, generate them with LLM
        questions = payload.questions_json
        if not questions:
            cur.execute(
                "SELECT title, summary, target_users, problem_statement FROM requirement_cards WHERE id = %s",
                (payload.requirement_card_id,),
            )
            req = cur.fetchone()
            req_card = {
                "title": req[0] or "",
                "summary": req[1] or "",
                "target_users": req[2] or "",
                "problem_statement": req[3] or "",
            }
            result = generate_questions(req_card)
            questions = result.get("questions", [])

        cur.execute(
            "SELECT COALESCE(MAX(round_no), 0) + 1 FROM clarification_rounds WHERE project_id = %s",
            (project_id,),
        )
        round_no = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO clarification_rounds (
                project_id, requirement_card_id, round_no, questions_json, answers_json, resolved_json, status
            )
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, '{}'::jsonb, 'open')
            RETURNING id, project_id, requirement_card_id, round_no, questions_json, answers_json, status, created_at, updated_at
            """,
            (
                project_id,
                payload.requirement_card_id,
                round_no,
                psycopg.types.json.Json(questions),
                psycopg.types.json.Json(payload.answers_json),
            ),
        )
        created = cur.fetchone()

        advance_stage(project_id, "requirement", "clarification", "clarification_created", conn=conn)
        conn.commit()
        cur.close()

    return {
        "id": created[0], "project_id": created[1],
        "requirement_card_id": created[2], "round_no": created[3],
        "questions_json": created[4], "answers_json": created[5],
        "status": created[6],
        "created_at": created[7].isoformat() if created[7] else None,
        "updated_at": created[8].isoformat() if created[8] else None,
    }


@router.get("/by-project/{project_id}")
def list_clarifications_by_project(project_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, requirement_card_id, round_no, questions_json, answers_json, resolved_json, status, created_at, updated_at
            FROM clarification_rounds
            WHERE project_id = %s
            ORDER BY round_no ASC, id ASC
            """,
            (project_id,),
        )
        rows = cur.fetchall()
        cur.close()

    return {
        "items": [
            {
                "id": r[0], "requirement_card_id": r[1], "round_no": r[2],
                "questions_json": r[3], "answers_json": r[4], "resolved_json": r[5],
                "status": r[6],
                "created_at": r[7].isoformat() if r[7] else None,
                "updated_at": r[8].isoformat() if r[8] else None,
            }
            for r in rows
        ],
        "count": len(rows),
    }


@router.post("/{clarification_id}/reply")
def reply_clarification(clarification_id: int, payload: ClarificationReply):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE clarification_rounds
            SET answers_json = %s::jsonb, status = 'answered', updated_at = NOW()
            WHERE id = %s
            RETURNING id, project_id, requirement_card_id, round_no, questions_json, answers_json, status, created_at, updated_at
            """,
            (psycopg.types.json.Json(payload.answers_json), clarification_id),
        )
        row = cur.fetchone()
        if not row:
            not_found("clarification", clarification_id)

        # Use LLM to refine the requirement card based on answers
        req_card_id = row[2]
        cur.execute(
            "SELECT title, summary, target_users, problem_statement FROM requirement_cards WHERE id = %s",
            (req_card_id,),
        )
        req = cur.fetchone()
        if req:
            req_card = {
                "title": req[0] or "", "summary": req[1] or "",
                "target_users": req[2] or "", "problem_statement": req[3] or "",
            }
            refined = refine_requirement(req_card, payload.answers_json)
            # Update requirement card with refined data
            cur.execute(
                """
                UPDATE requirement_cards
                SET title = COALESCE(%s, title), summary = COALESCE(%s, summary),
                    target_users = COALESCE(%s, target_users), problem_statement = COALESCE(%s, problem_statement),
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    refined.get("title"), refined.get("summary"),
                    refined.get("target_users"), refined.get("problem_statement"),
                    req_card_id,
                ),
            )

        conn.commit()
        cur.close()

    return {
        "id": row[0], "project_id": row[1],
        "requirement_card_id": row[2], "round_no": row[3],
        "questions_json": row[4], "answers_json": row[5],
        "status": row[6],
        "created_at": row[7].isoformat() if row[7] else None,
        "updated_at": row[8].isoformat() if row[8] else None,
    }


@router.post("/{clarification_id}/resolve")
def resolve_clarification(clarification_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE clarification_rounds
            SET status = 'resolved', resolved_json = '{"resolved": true}'::jsonb, updated_at = NOW()
            WHERE id = %s
            RETURNING id, project_id, requirement_card_id
            """,
            (clarification_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("clarification", clarification_id)

        project_id = row[1]
        advance_stage(project_id, "clarification", "prototype", "clarification_resolved", conn=conn)
        conn.commit()
        cur.close()

    return {
        "ok": True,
        "clarification_id": clarification_id,
        "project_id": project_id,
        "current_stage_key": "prototype",
    }
