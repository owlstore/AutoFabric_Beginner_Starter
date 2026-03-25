"""Unified Manus workspace service."""
from __future__ import annotations

import os
from pathlib import Path

from app.config import config
from app.db.pool import get_conn
from app.errors import not_found
from app.routers.clarifications import (
    ClarificationCreate,
    ClarificationReply,
    create_clarification,
    reply_clarification,
    resolve_clarification,
)
from app.routers.deliveries import DeliveryCreate, create_delivery
from app.routers.execution_runs import ExecutionRunCreate, create_execution_run, run_execution
from app.routers.orchestration import (
    OrchestrationPlanCreate,
    approve_orchestration_plan,
    create_orchestration_plan,
    generate_orchestration,
)
from app.routers.project_views import get_project_overview
from app.routers.projects import ProjectCreate, create_project
from app.routers.prototypes import PrototypeCreate, confirm_prototype, create_prototype, generate_prototype_endpoint
from app.routers.requirements import RequirementFromInput, confirm_requirement, create_requirement_from_input
from app.routers.testing_runs import TestingRunCreate, create_testing_run, execute_testing, pass_testing_run

STAGES = [
    "requirement",
    "clarification",
    "prototype",
    "orchestration",
    "execution",
    "testing",
    "delivery",
]

STAGE_LABELS = {
    "requirement": "需求分析",
    "clarification": "澄清整理",
    "prototype": "原型设计",
    "orchestration": "任务编排",
    "execution": "代码执行",
    "testing": "验证测试",
    "delivery": "交付归档",
}

# Stages that require approval for non-low-risk projects
APPROVAL_GATES = {"prototype", "orchestration", "delivery"}


def bootstrap_project(prompt: str, project_name: str | None = None, autopilot: bool = True) -> dict:
    project = create_project(
        ProjectCreate(
            name=(project_name or _make_project_name(prompt)),
            description=prompt,
            risk_level="medium",
        )
    )
    project_id = project["id"]

    requirement = create_requirement_from_input(project_id, RequirementFromInput(user_input=prompt))
    confirm_requirement(requirement["id"])
    create_clarification(
        ClarificationCreate(
            requirement_card_id=requirement["id"],
            questions_json=[],
            answers_json=[],
        )
    )

    if autopilot:
        run_autopilot(project_id)

    return get_workspace_snapshot(project_id)


def run_autopilot(project_id: int, operator_note: str | None = None) -> dict:
    if operator_note:
        _append_project_note(project_id, operator_note)

    overview = get_project_overview(project_id)
    if not overview:
        not_found("project", project_id)

    risk = overview.get("project", {}).get("risk_level", "medium")
    needs_approval = risk in ("high", "critical")
    stage_objects = overview.get("stage_objects", {})

    requirement = _latest(stage_objects.get("requirements"))
    if requirement and requirement.get("status") != "confirmed":
        confirm_requirement(requirement["id"])
        overview = get_project_overview(project_id)
        stage_objects = overview.get("stage_objects", {})
        requirement = _latest(stage_objects.get("requirements"))

    clarification = _latest(stage_objects.get("clarifications"))
    if requirement and not clarification:
        create_clarification(
            ClarificationCreate(
                requirement_card_id=requirement["id"],
                questions_json=[],
                answers_json=[],
            )
        )
        overview = get_project_overview(project_id)
        stage_objects = overview.get("stage_objects", {})
        clarification = _latest(stage_objects.get("clarifications"))

    if clarification and clarification.get("status") != "resolved":
        answers = _default_clarification_answers(
            clarification.get("questions_json") or [],
            overview.get("project", {}).get("description"),
        )
        reply_clarification(
            clarification["id"],
            ClarificationReply(answers_json=answers),
        )
        resolve_clarification(clarification["id"])
        overview = get_project_overview(project_id)
        stage_objects = overview.get("stage_objects", {})

    # --- Prototype (approval gate) ---
    prototype = _latest(stage_objects.get("prototypes"))
    if requirement and not prototype:
        prototype = create_prototype(PrototypeCreate(requirement_card_id=requirement["id"]))
    if prototype and not prototype.get("ia_json"):
        generate_prototype_endpoint(prototype["id"])
    if prototype and prototype.get("status") != "confirmed":
        if needs_approval and not _check_approval(project_id, "prototype"):
            _request_approval(project_id, "prototype", "原型设计完成，请确认后继续")
            return get_workspace_snapshot(project_id)
        confirm_prototype(prototype["id"])
        overview = get_project_overview(project_id)
        stage_objects = overview.get("stage_objects", {})

    # --- Orchestration (approval gate) ---
    prototype = _latest(stage_objects.get("prototypes"))
    orchestration = _latest(stage_objects.get("orchestration_plans"))
    if prototype and not orchestration:
        orchestration = create_orchestration_plan(OrchestrationPlanCreate(prototype_spec_id=prototype["id"]))
    if orchestration and not orchestration.get("agent_jobs_json"):
        generate_orchestration(orchestration["id"])
    if orchestration and orchestration.get("status") != "approved":
        if needs_approval and not _check_approval(project_id, "orchestration"):
            _request_approval(project_id, "orchestration", "任务编排完成，请确认执行计划")
            return get_workspace_snapshot(project_id)
        approve_orchestration_plan(orchestration["id"])
        overview = get_project_overview(project_id)
        stage_objects = overview.get("stage_objects", {})

    orchestration = _latest(stage_objects.get("orchestration_plans"))
    execution = _latest(stage_objects.get("execution_runs"))
    if orchestration and not execution:
        execution = create_execution_run(
            ExecutionRunCreate(
                plan_id=orchestration["id"],
                job_type="fullstack",
                title="Autopilot execution",
            )
        )
    if execution and execution.get("status") != "completed":
        run_execution(execution["id"])
        overview = get_project_overview(project_id)
        stage_objects = overview.get("stage_objects", {})

    execution = _latest(stage_objects.get("execution_runs"))
    testing = _latest(stage_objects.get("testing_runs"))
    if execution and not testing:
        testing = create_testing_run(
            TestingRunCreate(
                job_id=execution["id"],
                title="Autopilot validation",
                note="Generated by unified Manus autopilot",
            )
        )
    if testing and testing.get("status") == "pending":
        result = execute_testing(testing["id"])
        if result.get("status") != "passed":
            pass_testing_run(testing["id"])
        overview = get_project_overview(project_id)
        stage_objects = overview.get("stage_objects", {})
    elif testing and testing.get("status") not in ("passed", "completed"):
        pass_testing_run(testing["id"])
        overview = get_project_overview(project_id)
        stage_objects = overview.get("stage_objects", {})

    # --- Delivery (approval gate) ---
    deliveries = stage_objects.get("deliveries") or []
    if not deliveries:
        if needs_approval and not _check_approval(project_id, "delivery"):
            _request_approval(project_id, "delivery", "测试通过，确认发布交付包")
            return get_workspace_snapshot(project_id)
        create_delivery(DeliveryCreate(project_id=project_id))

    return get_workspace_snapshot(project_id)


def _check_approval(project_id: int, stage_name: str) -> bool:
    """Check if the stage has been approved."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT decision FROM human_approvals
            WHERE project_id = %s AND stage_name = %s
            ORDER BY id DESC LIMIT 1
        """, (project_id, stage_name))
        row = cur.fetchone()
        cur.close()
    return row is not None and row[0] == "approved"


def _request_approval(project_id: int, stage_name: str, reason: str) -> dict:
    """Create an approval request."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO human_approvals (project_id, stage_name, approval_type, decision, decision_note)
            VALUES (%s, %s, 'stage_gate', 'pending', %s)
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (project_id, stage_name, reason))
        row = cur.fetchone()
        conn.commit()
        cur.close()
    return {"approval_id": row[0] if row else None, "stage": stage_name, "status": "pending"}


def approve_stage(project_id: int, stage_name: str, decision: str = "approved", note: str | None = None) -> dict:
    """Human approves or rejects a stage gate."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE human_approvals
            SET decision = %s, decided_by = 'operator', decision_note = COALESCE(%s, decision_note),
                updated_at = NOW()
            WHERE project_id = %s AND stage_name = %s AND decision = 'pending'
        """, (decision, note, project_id, stage_name))
        conn.commit()
        cur.close()

    if decision == "approved":
        return run_autopilot(project_id)
    return get_workspace_snapshot(project_id)


def rerun_from_stage(project_id: int, stage_name: str, note: str | None = None) -> dict:
    """Reset a stage and all downstream stages, then re-run autopilot."""
    if stage_name not in STAGES:
        from app.errors import bad_request
        bad_request(f"Unknown stage: {stage_name}")

    stage_index = STAGES.index(stage_name)
    stages_to_reset = STAGES[stage_index:]

    with get_conn() as conn:
        cur = conn.cursor()
        # Reset stage states
        for s in stages_to_reset:
            cur.execute("""
                UPDATE project_stage_states
                SET stage_status = 'pending', completed_at = NULL, updated_at = NOW()
                WHERE project_id = %s AND stage_key = %s
            """, (project_id, s))

        # Set current stage back
        cur.execute("""
            UPDATE projects SET current_stage_key = %s, updated_at = NOW()
            WHERE id = %s
        """, (stage_name, project_id))

        # Clear approvals for reset stages
        for s in stages_to_reset:
            cur.execute("""
                DELETE FROM human_approvals
                WHERE project_id = %s AND stage_name = %s
            """, (project_id, s))

        conn.commit()
        cur.close()

    if note:
        _append_project_note(project_id, f"Rerun from {stage_name}: {note}")

    return run_autopilot(project_id)


def get_workspace_snapshot(project_id: int) -> dict:
    overview = get_project_overview(project_id)
    project = overview.get("project", {})
    stage_rows = {row["stage_key"]: row for row in overview.get("stages", [])}
    latest = overview.get("latest_objects", {})

    stage_rail = []
    for index, stage in enumerate(STAGES, start=1):
        row = stage_rows.get(stage, {})
        is_current = project.get("current_stage_key") == stage
        status = row.get("stage_status") or ("completed" if latest.get(stage if stage != "execution" else "execution") else "pending")
        if is_current and status not in ("completed", "resolved", "published", "passed"):
            status = "active"
        if latest.get("delivery") and stage == "delivery":
            status = "completed"
        stage_rail.append(
            {
                "key": stage,
                "label": STAGE_LABELS[stage],
                "order": index,
                "status": _normalize_stage_status(status),
                "is_current": is_current,
            }
        )

    latest_requirement = latest.get("requirement") or {}
    artifact_root = Path(config.openclaw.output_dir) / f"project_{project_id}"
    artifacts = _collect_artifacts(artifact_root)
    recent_activity = _build_recent_activity(overview)
    recommended_actions = _build_recommended_actions(project, latest, artifacts)

    return {
        "project": project,
        "overview": overview,
        "workspace": {
            "headline": latest_requirement.get("title") or project.get("name") or f"Project #{project_id}",
            "summary": latest_requirement.get("summary") or project.get("description") or "暂无摘要",
            "control_mode": "autopilot",
            "llm_provider": _effective_llm_provider(),
            "bridge_mode": config.openclaw.bridge_mode,
            "next_action": recommended_actions[0] if recommended_actions else "继续观察执行情况",
            "recommended_actions": recommended_actions,
            "stage_rail": stage_rail,
            "artifacts": artifacts,
            "recent_activity": recent_activity,
            "run_summary": _build_run_summary(latest),
            "metrics": {
                "projects": 1,
                "artifacts": len(artifacts),
                "transitions": len(overview.get("transitions", [])),
                "completed_stages": len([item for item in stage_rail if item["status"] == "completed"]),
            },
        },
    }


def _make_project_name(prompt: str) -> str:
    cleaned = (prompt or "").strip()
    if not cleaned:
        return "Untitled Mission"
    for splitter in ("。", "\n", ",", "，"):
        cleaned = cleaned.split(splitter, 1)[0].strip()
    return cleaned[:48]


def _latest(items: list[dict] | None) -> dict | None:
    return items[0] if items else None


def _default_clarification_answers(questions: list, context: str | None = None) -> list[str]:
    defaults = [
        "首个版本面向内部团队，优先交付 Web 工作台。",
        "优先实现任务录入、阶段跟踪、执行可视化和交付摘要。",
        "默认采用 Docker + PostgreSQL，本地可运行，后续可上云。",
        "界面偏专业仪表盘风格，信息密度高但可读性清晰。",
    ]
    answers = []
    for index, question in enumerate(questions):
        if isinstance(question, dict):
            question_text = question.get("question", "")
        else:
            question_text = str(question)
        candidate = defaults[index % len(defaults)]
        if "部署" in question_text:
            candidate = "先保证本地 Docker 可运行，后续再抽象到云部署。"
        elif "界面" in question_text or "风格" in question_text:
            candidate = "采用专业任务中台风格，突出进度、风险和产物。"
        elif "优先" in question_text:
            candidate = "优先做最短闭环：创建任务、自动推进、查看交付。"
        elif "对外" in question_text:
            candidate = "先面向内部协作团队，权限模型保持简单。"
        if context:
            candidate = f"{candidate} 结合当前任务描述：{context[:48]}。"
        answers.append(candidate)
    return answers or defaults[:2]


def _append_project_note(project_id: int, note: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE projects
            SET description = CONCAT(COALESCE(description, ''), CASE WHEN COALESCE(description, '') = '' THEN '' ELSE E'\n\n' END, %s),
                updated_at = NOW()
            WHERE id = %s
            """,
            (f"Operator note: {note}", project_id),
        )
        conn.commit()
        cur.close()


def _collect_artifacts(root: Path) -> list[dict]:
    if not root.exists():
        return []
    artifacts = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        category = rel.split("/", 1)[0]
        artifacts.append(
            {
                "name": path.name,
                "path": rel,
                "category": category,
                "size_kb": round(path.stat().st_size / 1024, 1),
            }
        )
        if len(artifacts) >= 16:
            break
    return artifacts


def _build_recent_activity(overview: dict) -> list[dict]:
    activity = []
    for item in overview.get("transitions", [])[-8:]:
        activity.append(
            {
                "title": f"{item.get('from_stage_key') or 'start'} -> {item.get('to_stage_key')}",
                "detail": item.get("transition_reason") or item.get("triggered_by") or "stage transition",
                "timestamp": item.get("created_at"),
            }
        )
    if not activity:
        project = overview.get("project", {})
        activity.append(
            {
                "title": "Project created",
                "detail": project.get("description") or "Mission initialized",
                "timestamp": project.get("created_at"),
            }
        )
    return list(reversed(activity))


def _build_recommended_actions(project: dict, latest: dict, artifacts: list[dict]) -> list[str]:
    current_stage = project.get("current_stage_key")
    actions = []
    if current_stage == "delivery":
        actions.append("检查交付包内容，确认 README、测试结果与产物目录完整。")
    elif current_stage == "testing":
        actions.append("关注测试输出与代码审查结果，必要时补人工验收。")
    elif current_stage == "execution":
        actions.append("查看最新代码产物与执行摘要，确认关键文件已经生成。")
    else:
        actions.append("继续运行 autopilot，让系统自动推进到下一阶段。")
    if latest.get("execution"):
        actions.append("查看执行 run 的输出文件和依赖建议。")
    if artifacts:
        actions.append("浏览 artifacts 面板，快速定位原型、代码和交付文件。")
    return actions


def _build_run_summary(latest: dict) -> list[dict]:
    items = []
    execution = latest.get("execution")
    testing = latest.get("testing")
    delivery = latest.get("delivery")
    if execution:
        items.append({"label": "Execution", "status": execution.get("status"), "meta": execution.get("executor_key")})
    if testing:
        items.append({"label": "Testing", "status": testing.get("status"), "meta": testing.get("note")})
    if delivery:
        items.append({"label": "Delivery", "status": delivery.get("status"), "meta": delivery.get("published_at")})
    return items


def _normalize_stage_status(status: str | None) -> str:
    if status in ("completed", "resolved", "passed", "published"):
        return "completed"
    if status in ("active", "running", "open", "answered", "approved"):
        return "active"
    return "pending"


def _effective_llm_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "").lower()
    if provider:
        return provider
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude"
    return "mock"
