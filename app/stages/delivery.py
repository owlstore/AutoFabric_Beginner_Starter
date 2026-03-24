"""Stage 7: Delivery — generate documentation, configs, and package everything."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from app.llm import get_llm
from app.config import config

DOCS_PROMPT = """\
你是一名技术文档工程师。为以下项目生成完整的项目文档。

输出 JSON：
{
  "readme": "完整的 README.md 内容（Markdown 格式，包含项目介绍、安装、使用、API 文档等）",
  "api_docs": "API 文档内容（包含每个端点的详细说明）",
  "architecture": "架构文档内容（包含 Mermaid 图）",
  "changelog": "CHANGELOG.md 内容"
}"""

DEPLOY_PROMPT = """\
你是一名 DevOps 工程师。为以下项目生成部署配置文件。

输出 JSON：
{
  "dockerfile": "Dockerfile 内容",
  "docker_compose": "docker-compose.yml 内容",
  "ci_workflow": "GitHub Actions CI 配置内容",
  "env_example": ".env.example 内容"
}"""


def generate_docs(
    requirement_card: dict,
    api_design: list[dict] | None = None,
    architecture: dict | None = None,
) -> dict:
    """Generate project documentation using LLM."""
    llm = get_llm()
    parts = [f"需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}"]
    if api_design:
        parts.append(f"API 设计：\n{json.dumps(api_design, ensure_ascii=False, indent=2)}")
    if architecture:
        parts.append(f"架构设计：\n{json.dumps(architecture, ensure_ascii=False, indent=2)}")
    return llm.complete_json(
        system=DOCS_PROMPT,
        user="\n\n".join(parts),
        tier="fast",
        max_tokens=6000,
    )


def generate_deploy_config(
    requirement_card: dict,
    tech_stack: dict | None = None,
) -> dict:
    """Generate deployment configuration files using LLM."""
    llm = get_llm()
    parts = [f"需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}"]
    if tech_stack:
        parts.append(f"技术栈：\n{json.dumps(tech_stack, ensure_ascii=False, indent=2)}")
    return llm.complete_json(
        system=DEPLOY_PROMPT,
        user="\n\n".join(parts),
        tier="fast",
        max_tokens=4000,
    )


def assemble_delivery(project_id: int, docs: dict, deploy: dict) -> str:
    """Assemble final delivery package on disk. Returns delivery directory path."""
    output_dir = config.openclaw.output_dir
    project_dir = Path(output_dir) / f"project_{project_id}"
    delivery_dir = project_dir / "delivery_package"
    delivery_dir.mkdir(parents=True, exist_ok=True)

    # Copy source code
    src_dir = project_dir / "src"
    if src_dir.exists():
        dest_src = delivery_dir / "src"
        if dest_src.exists():
            shutil.rmtree(dest_src)
        shutil.copytree(src_dir, dest_src)

    # Copy tests
    tests_dir = project_dir / "tests"
    if tests_dir.exists():
        dest_tests = delivery_dir / "tests"
        if dest_tests.exists():
            shutil.rmtree(dest_tests)
        shutil.copytree(tests_dir, dest_tests)

    # Copy prototype
    proto_dir = project_dir / "prototype"
    if proto_dir.exists():
        dest_proto = delivery_dir / "prototype"
        if dest_proto.exists():
            shutil.rmtree(dest_proto)
        shutil.copytree(proto_dir, dest_proto)

    # Write documentation
    docs_dir = delivery_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    _write_if(delivery_dir / "README.md", docs.get("readme"))
    _write_if(docs_dir / "API.md", docs.get("api_docs"))
    _write_if(docs_dir / "ARCHITECTURE.md", docs.get("architecture"))
    _write_if(delivery_dir / "CHANGELOG.md", docs.get("changelog"))

    # Write deploy configs
    _write_if(delivery_dir / "Dockerfile", deploy.get("dockerfile"))
    _write_if(delivery_dir / "docker-compose.yml", deploy.get("docker_compose"))

    github_dir = delivery_dir / ".github" / "workflows"
    github_dir.mkdir(parents=True, exist_ok=True)
    _write_if(github_dir / "ci.yml", deploy.get("ci_workflow"))

    _write_if(delivery_dir / ".env.example", deploy.get("env_example"))

    return str(delivery_dir)


def _write_if(path: Path, content: str | None) -> None:
    """Write file only if content is not empty."""
    if content:
        path.write_text(content, encoding="utf-8")
