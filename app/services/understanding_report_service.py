from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _classify_architecture(data: dict[str, Any]) -> str:
    markers = data.get("markers", {})
    top_level = data.get("top_level", {})
    dirs = set(top_level.get("dirs", []))

    has_backend = "app" in dirs
    has_frontend = "frontend" in dirs
    has_migrations = "alembic" in dirs
    has_tests = "tests" in dirs

    if has_backend and has_frontend:
        return "前后端分离/混合仓一体化项目"
    if has_backend:
        return "后端服务型项目"
    if has_frontend:
        return "前端项目"
    return "待进一步识别的通用工程项目"


def _describe_top_level(data: dict[str, Any]) -> list[str]:
    dirs = set(data.get("top_level", {}).get("dirs", []))
    descriptions = []

    mapping = [
        ("app", "后端主应用目录，通常包含接口、服务、模型、数据库访问等核心逻辑。"),
        ("frontend", "前端应用目录，通常包含页面、构建配置和前端依赖。"),
        ("alembic", "数据库迁移目录，用于管理 schema 演进。"),
        ("tests", "测试目录，用于放置 smoke test、单元测试或集成测试。"),
        ("scripts", "脚本目录，用于本地初始化、运行、校验、数据修复等辅助操作。"),
        ("sql", "原始 SQL 或阶段性数据库脚本目录。"),
        (".autofabric_runs", "运行产物目录，用于存放 outcome 执行后的中间结果和工件。"),
    ]

    for name, desc in mapping:
        if name in dirs:
            descriptions.append(f"- `{name}/`：{desc}")

    return descriptions


def build_understanding_report(outcome_id: int, workspace_dir: str) -> str:
    workspace = Path(workspace_dir)
    summary_path = workspace / "analysis_summary.json"
    data = _read_json(summary_path)

    architecture = _classify_architecture(data)
    markers = data.get("markers", {})
    code_files = data.get("code_files", [])[:12]

    lines: list[str] = []
    lines.append(f"# Understanding Report - Outcome {outcome_id}")
    lines.append("")
    lines.append("## 1. 项目总体判断")
    lines.append(f"- 目标：{data.get('goal_text')}")
    lines.append(f"- 项目路径：`{data.get('project_path')}`")
    lines.append(f"- 初始识别类型：`{data.get('system_type')}`")
    lines.append(f"- 架构判断：{architecture}")
    lines.append("")

    lines.append("## 2. 顶层结构说明")
    lines.extend(_describe_top_level(data))
    lines.append("")

    lines.append("## 3. 关键标记文件/目录")
    for key, value in markers.items():
        lines.append(f"- `{key}`: {'存在' if value else '不存在'}")
    lines.append("")

    lines.append("## 4. 代表性文件")
    for f in code_files:
        lines.append(f"- `{f}`")
    lines.append("")

    lines.append("## 5. 初步架构结论")
    lines.append("- 当前仓库不是单一脚本项目，而是具备后端、前端、数据库迁移、测试与脚本目录的工程化项目。")
    if "app" in data.get("top_level", {}).get("dirs", []):
        lines.append("- `app/` 很可能是后端主入口区域，后续应继续识别其中的 `main.py`、services、models、db 等结构。")
    if "frontend" in data.get("top_level", {}).get("dirs", []):
        lines.append("- `frontend/` 表明系统存在前端界面层，后续应识别其入口、页面结构与 API 对接方式。")
    if "alembic" in data.get("top_level", {}).get("dirs", []):
        lines.append("- `alembic/` 表明数据库 schema 受迁移系统管理，数据库演进已具备工程基础。")
    lines.append("")

    lines.append("## 6. 下一步建议")
    lines.append("- 识别后端入口文件与路由注册位置。")
    lines.append("- 识别 services / models / db 的职责边界。")
    lines.append("- 梳理 frontend 与 backend 的交互边界。")
    lines.append("- 输出系统架构图、逻辑图与模块职责说明。")
    lines.append("")

    report = "\n".join(lines)
    report_path = workspace / "understanding_report.md"
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)
