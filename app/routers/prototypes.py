from fastapi import APIRouter
from pydantic import BaseModel
import psycopg.types.json

from app.db.pool import get_conn
from app.errors import not_found, bad_request
from app.services.stage_executor import advance_stage
from app.stages.prototype import design_ia, design_modules, generate_ui_prototype, write_prototype_files

router = APIRouter(prefix="/prototypes", tags=["prototypes"])


class PrototypeCreate(BaseModel):
    requirement_card_id: int | None = None
    ia_json: dict | None = None
    page_flow_json: dict | None = None
    module_map_json: dict | None = None
    api_draft_json: dict | None = None
    figma_url: str | None = None


@router.post("")
def create_prototype(payload: PrototypeCreate):
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

        cur.execute(
            "SELECT COALESCE(MAX(version_no), 0) + 1 FROM prototype_specs WHERE project_id = %s",
            (project_id,),
        )
        version_no = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO prototype_specs (
                project_id, requirement_card_id, version_no,
                ia_json, page_flow_json, module_map_json, api_draft_json,
                figma_url, status
            )
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s, 'draft')
            RETURNING id, project_id, requirement_card_id, version_no, ia_json, page_flow_json, module_map_json, api_draft_json, figma_url, status, created_at, updated_at
            """,
            (
                project_id, payload.requirement_card_id, version_no,
                psycopg.types.json.Json(payload.ia_json or {}),
                psycopg.types.json.Json(payload.page_flow_json or {}),
                psycopg.types.json.Json(payload.module_map_json or {}),
                psycopg.types.json.Json(payload.api_draft_json or {}),
                payload.figma_url,
            ),
        )
        created = cur.fetchone()

        advance_stage(project_id, "clarification", "prototype", "prototype_created", conn=conn)
        conn.commit()
        cur.close()

    return _row_to_proto(created)


@router.get("/by-project/{project_id}")
def list_prototypes_by_project(project_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, requirement_card_id, version_no, ia_json, page_flow_json, module_map_json, api_draft_json, figma_url, status, confirmed_at, created_at, updated_at
            FROM prototype_specs
            WHERE project_id = %s
            ORDER BY version_no DESC, id DESC
            """,
            (project_id,),
        )
        rows = cur.fetchall()
        cur.close()

    return {
        "items": [
            {
                "id": r[0], "requirement_card_id": r[1], "version_no": r[2],
                "ia_json": r[3], "page_flow_json": r[4], "module_map_json": r[5],
                "api_draft_json": r[6], "figma_url": r[7], "status": r[8],
                "confirmed_at": r[9].isoformat() if r[9] else None,
                "created_at": r[10].isoformat() if r[10] else None,
                "updated_at": r[11].isoformat() if r[11] else None,
            }
            for r in rows
        ],
        "count": len(rows),
    }


@router.post("/{prototype_id}/generate")
def generate_prototype_endpoint(prototype_id: int):
    """Use LLM to generate IA, modules, API design, and UI prototype code."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, project_id, requirement_card_id FROM prototype_specs WHERE id = %s",
            (prototype_id,),
        )
        proto = cur.fetchone()
        if not proto:
            not_found("prototype", prototype_id)

        project_id = proto[1]
        req_card_id = proto[2]

        # Fetch requirement card for LLM context
        cur.execute(
            "SELECT title, summary, target_users, problem_statement FROM requirement_cards WHERE id = %s",
            (req_card_id,),
        )
        req = cur.fetchone()
        req_card = {
            "title": req[0] or "", "summary": req[1] or "",
            "target_users": req[2] or "", "problem_statement": req[3] or "",
        }

        # Step 1: Design IA
        ia = design_ia(req_card)

        # Step 2: Design modules + API
        modules = design_modules(req_card, ia)

        # Step 3: Generate UI prototype code
        ui_proto = generate_ui_prototype(req_card, ia, modules)

        # Step 4: Write files to disk
        proto_dir = write_prototype_files(project_id, ui_proto)

        # Update DB with generated data
        cur.execute(
            """
            UPDATE prototype_specs
            SET
                ia_json = %s::jsonb,
                page_flow_json = %s::jsonb,
                module_map_json = %s::jsonb,
                api_draft_json = %s::jsonb,
                updated_at = NOW()
            WHERE id = %s
            RETURNING id, project_id, version_no, ia_json, page_flow_json, module_map_json, api_draft_json, figma_url, status, created_at, updated_at
            """,
            (
                psycopg.types.json.Json(ia),
                psycopg.types.json.Json({"user_flows": ia.get("user_flows", []), "mermaid": modules.get("mermaid_architecture", "")}),
                psycopg.types.json.Json(modules.get("module_map", [])),
                psycopg.types.json.Json(modules.get("api_design", [])),
                prototype_id,
            ),
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()

    result = {
        "id": row[0], "project_id": row[1], "version_no": row[2],
        "ia_json": row[3], "page_flow_json": row[4], "module_map_json": row[5],
        "api_draft_json": row[6], "figma_url": row[7], "status": row[8],
        "created_at": row[9].isoformat() if row[9] else None,
        "updated_at": row[10].isoformat() if row[10] else None,
        "prototype_dir": proto_dir,
        "preview_url": f"/preview/{project_id}",
        "files_generated": len(ui_proto.get("files", [])),
    }
    return result


@router.post("/{prototype_id}/confirm")
def confirm_prototype(prototype_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE prototype_specs
            SET status = 'confirmed', confirmed_at = NOW(), updated_at = NOW()
            WHERE id = %s
            RETURNING id, project_id
            """,
            (prototype_id,),
        )
        row = cur.fetchone()
        if not row:
            not_found("prototype", prototype_id)

        project_id = row[1]
        advance_stage(
            project_id, "prototype", "orchestration", "prototype_confirmed",
            conn=conn,
            approval={
                "approval_type": "prototype_confirm",
                "target_ref_type": "prototype_spec",
                "target_ref_id": prototype_id,
                "note": "Prototype confirmed",
            },
        )
        conn.commit()
        cur.close()

    return {
        "ok": True,
        "prototype_id": prototype_id,
        "project_id": project_id,
        "current_stage_key": "orchestration",
    }


def _row_to_proto(r):
    return {
        "id": r[0], "project_id": r[1], "requirement_card_id": r[2],
        "version_no": r[3], "ia_json": r[4], "page_flow_json": r[5],
        "module_map_json": r[6], "api_draft_json": r[7], "figma_url": r[8],
        "status": r[9],
        "created_at": r[10].isoformat() if r[10] else None,
        "updated_at": r[11].isoformat() if r[11] else None,
    }
