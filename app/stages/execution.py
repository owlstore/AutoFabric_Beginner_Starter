"""Stage 5: Execution — LLM-powered code generation via OpenClaw bridge."""
from __future__ import annotations

import json
import os
from pathlib import Path

from app.llm import get_llm
from app.config import config

CODE_GEN_PROMPT = """\
你是高级全栈工程师。根据任务描述生成生产级代码。

要求：
1. 代码必须完整、可运行，不要留 TODO 或占位符
2. 遵循最佳实践（类型提示、错误处理、日志）
3. 文件路径使用相对路径（从项目根目录开始）
4. 如果任务涉及 API，确保请求/响应模型完整
5. 如果任务涉及数据库，包含 migration 或建表语句

输出 JSON：
{
  "files": [
    {"path": "相对文件路径", "content": "完整代码内容"},
    ...
  ],
  "summary": "本次实现的简要说明",
  "dependencies": ["新增的依赖包名"],
  "notes": "注意事项或后续建议"
}"""


def execute_job(
    job: dict,
    project_id: int,
    context_files: list[dict] | None = None,
) -> dict:
    """Execute a single job by generating code with LLM."""
    llm = get_llm()
    parts = [f"任务：\n{json.dumps(job, ensure_ascii=False, indent=2)}"]
    if context_files:
        file_list = "\n".join(
            f"- {f['path']}" for f in context_files[:20]  # limit context size
        )
        parts.append(f"已有文件：\n{file_list}")

    result = llm.complete_json(
        system=CODE_GEN_PROMPT,
        user="\n\n".join(parts),
        tier="strong",
        max_tokens=16000,
    )
    return result


def write_job_output(project_id: int, job_id: str, result: dict) -> list[str]:
    """Write generated files to disk. Returns list of written file paths."""
    output_dir = config.openclaw.output_dir
    project_dir = Path(output_dir) / f"project_{project_id}" / "src"
    project_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for file_info in result.get("files", []):
        rel_path = file_info["path"]
        full_path = project_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(file_info["content"], encoding="utf-8")
        written.append(str(full_path))
    return written


def execute_plan(project_id: int, jobs: list[dict]) -> dict:
    """Execute all jobs in order, accumulating context."""
    results = []
    all_files: list[dict] = []

    for job in jobs:
        result = execute_job(job, project_id, context_files=all_files)
        written = write_job_output(project_id, job["job_id"], result)

        # Accumulate generated files as context for subsequent jobs
        for f in result.get("files", []):
            all_files.append({"path": f["path"]})

        results.append({
            "job_id": job["job_id"],
            "status": "completed",
            "files_written": written,
            "summary": result.get("summary", ""),
            "dependencies": result.get("dependencies", []),
        })

    return {
        "project_id": project_id,
        "total_jobs": len(jobs),
        "completed": len(results),
        "job_results": results,
    }
