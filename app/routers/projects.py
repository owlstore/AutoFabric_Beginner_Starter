from fastapi import APIRouter
from pydantic import BaseModel

from app.db.pool import get_conn
from app.errors import not_found

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    risk_level: str | None = "medium"


def _row_to_project(r):
    return {
        "id": r[0],
        "name": r[1],
        "description": r[2],
        "current_stage_key": r[3],
        "status": r[4],
        "risk_level": r[5],
        "created_at": r[6].isoformat() if r[6] else None,
        "updated_at": r[7].isoformat() if r[7] else None,
    }


@router.get("")
def list_projects():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, description, current_stage_key, status, risk_level, created_at, updated_at
            FROM projects
            ORDER BY id DESC
        """)
        rows = cur.fetchall()
        cur.close()
    return {"items": [_row_to_project(r) for r in rows], "count": len(rows)}


@router.post("")
def create_project(payload: ProjectCreate):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO projects (name, description, current_stage_key, status, risk_level)
            VALUES (%s, %s, 'requirement', 'active', %s)
            RETURNING id, name, description, current_stage_key, status, risk_level, created_at, updated_at
        """, (payload.name, payload.description, payload.risk_level or "medium"))
        row = cur.fetchone()

        cur.execute("""
            INSERT INTO project_stage_states (project_id, stage_key, stage_status, is_current, entered_at)
            VALUES (%s, 'requirement', 'active', TRUE, NOW())
            ON CONFLICT (project_id, stage_key) DO NOTHING
        """, (row[0],))

        conn.commit()
        cur.close()
    return _row_to_project(row)


@router.get("/{project_id}")
def get_project(project_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, description, current_stage_key, status, risk_level, created_at, updated_at
            FROM projects
            WHERE id = %s
        """, (project_id,))
        row = cur.fetchone()
        if not row:
            not_found("project", project_id)

        cur.execute("""
            SELECT id, version_no, title, summary, status, confirmed_at, created_at, updated_at
            FROM requirement_cards
            WHERE project_id = %s
            ORDER BY version_no DESC, id DESC
        """, (project_id,))
        req_rows = cur.fetchall()
        cur.close()

    result = _row_to_project(row)
    result["requirements"] = [
        {
            "id": r[0], "version_no": r[1], "title": r[2], "summary": r[3],
            "status": r[4],
            "confirmed_at": r[5].isoformat() if r[5] else None,
            "created_at": r[6].isoformat() if r[6] else None,
            "updated_at": r[7].isoformat() if r[7] else None,
        }
        for r in req_rows
    ]
    return result
