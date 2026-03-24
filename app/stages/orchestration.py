"""Stage 4: Orchestration Planner — LLM decomposes requirements into executable tasks."""
from __future__ import annotations

import json

from app.llm import get_llm

ORCHESTRATION_PROMPT = """\
你是一名技术项目经理。将需求和原型规格拆解为可执行的开发任务。

每个任务必须包含足够的上下文让开发者独立完成。
任务之间要明确依赖关系和执行顺序。

输出 JSON：
{
  "epic": "项目名称",
  "features": [
    {
      "name": "功能模块名",
      "tasks": [
        {
          "key": "唯一标识（snake_case）",
          "name": "任务名称",
          "executor": "backend_builder|frontend_builder|fullstack_builder|test_writer",
          "depends_on": ["依赖的任务key"],
          "description": "详细描述（包含具体实现要点）",
          "estimated_files": ["预期生成的文件路径"],
          "required_skills": ["python", "react", "sql"],
          "acceptance_criteria": ["验收条件1", "验收条件2"]
        }
      ]
    }
  ],
  "execution_order": ["task_key_1", "task_key_2", "..."],
  "risk_notes": ["风险提示"]
}"""


def plan_orchestration(
    requirement_card: dict,
    ia: dict | None = None,
    modules: dict | None = None,
) -> dict:
    """Generate an orchestration plan with executable tasks."""
    llm = get_llm()
    parts = [f"需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}"]
    if ia:
        parts.append(f"信息架构：\n{json.dumps(ia, ensure_ascii=False, indent=2)}")
    if modules:
        parts.append(f"模块设计：\n{json.dumps(modules, ensure_ascii=False, indent=2)}")
    return llm.complete_json(
        system=ORCHESTRATION_PROMPT,
        user="\n\n".join(parts),
        tier="strong",
        max_tokens=4096,
    )


def to_openclaw_jobs(plan: dict) -> list[dict]:
    """Convert orchestration plan to OpenClaw bridge job format."""
    jobs = []
    for feature in plan.get("features", []):
        for task in feature.get("tasks", []):
            jobs.append({
                "job_id": task["key"],
                "executor": task.get("executor", "fullstack_builder"),
                "payload": {
                    "task_name": task["name"],
                    "description": task.get("description", ""),
                    "estimated_files": task.get("estimated_files", []),
                    "required_skills": task.get("required_skills", []),
                    "acceptance_criteria": task.get("acceptance_criteria", []),
                },
                "depends_on": task.get("depends_on", []),
            })
    return jobs
