"""Shared stage advancement logic for Phase 2 routers.

Centralizes the repeated pattern of:
1. Update projects.current_stage_key
2. Insert/update project_stage_states
3. Mark previous stage as completed
4. Record stage_transition
5. Optionally record human_approval
"""
from __future__ import annotations

from app.db.pool import get_conn


def advance_stage(
    project_id: int,
    from_stage: str | None,
    to_stage: str,
    reason: str,
    triggered_by: str = "phase2_backend",
    *,
    conn=None,
    approval: dict | None = None,
):
    """Move a project to the next stage.

    Args:
        project_id: The project ID.
        from_stage: The stage being left (None for initial).
        to_stage: The stage being entered.
        reason: Why the transition happened (e.g. 'requirement_confirmed').
        triggered_by: Who triggered this (default 'phase2_backend').
        conn: Optional existing connection (caller manages commit).
               If None, creates a new connection and auto-commits.
        approval: Optional dict with keys:
            approval_type, target_ref_type, target_ref_id, note
    """
    own_conn = conn is None
    if own_conn:
        cm = get_conn()
        conn = cm.__enter__()

    cur = conn.cursor()

    # 1. Update project current stage
    cur.execute(
        "UPDATE projects SET current_stage_key = %s, updated_at = NOW() WHERE id = %s",
        (to_stage, project_id),
    )

    # 2. Activate the new stage
    cur.execute(
        """
        INSERT INTO project_stage_states (project_id, stage_key, stage_status, is_current, entered_at)
        VALUES (%s, %s, 'active', TRUE, NOW())
        ON CONFLICT (project_id, stage_key)
        DO UPDATE SET is_current = TRUE, stage_status = 'active', updated_at = NOW()
        """,
        (project_id, to_stage),
    )

    # 3. Deactivate previous stages and mark from_stage as completed
    if from_stage:
        cur.execute(
            """
            UPDATE project_stage_states
            SET is_current = FALSE,
                stage_status = CASE WHEN stage_key = %s THEN 'completed' ELSE stage_status END,
                exited_at = CASE WHEN stage_key = %s THEN NOW() ELSE exited_at END,
                updated_at = NOW()
            WHERE project_id = %s AND stage_key <> %s AND is_current = TRUE
            """,
            (from_stage, from_stage, project_id, to_stage),
        )
    else:
        cur.execute(
            """
            UPDATE project_stage_states
            SET is_current = FALSE, updated_at = NOW()
            WHERE project_id = %s AND stage_key <> %s AND is_current = TRUE
            """,
            (project_id, to_stage),
        )

    # 4. Record transition
    cur.execute(
        """
        INSERT INTO stage_transitions (project_id, from_stage_key, to_stage_key, transition_reason, triggered_by)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (project_id, from_stage, to_stage, reason, triggered_by),
    )

    # 5. Optional human approval record
    if approval:
        cur.execute(
            """
            INSERT INTO human_approvals (
                project_id, approval_type, target_ref_type, target_ref_id,
                decision, note, approved_by, approved_at
            )
            VALUES (%s, %s, %s, %s, 'approved', %s, 'local_user', NOW())
            """,
            (
                project_id,
                approval["approval_type"],
                approval["target_ref_type"],
                approval["target_ref_id"],
                approval.get("note", ""),
            ),
        )

    cur.close()

    if own_conn:
        conn.commit()
        cm.__exit__(None, None, None)
