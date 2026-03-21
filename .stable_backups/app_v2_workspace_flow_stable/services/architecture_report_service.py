from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_architecture_report(workspace_dir: str) -> str:
    workspace = Path(workspace_dir)

    analysis = _read_json(workspace / "analysis_summary.json")
    module_map = _read_json(workspace / "module_map.json")
    api_map = _read_json(workspace / "api_map.json")
    data_model_map = _read_json(workspace / "data_model_map.json")

    architecture = "未知"
    if analysis.get("system_type") == "fullstack_engineering_project":
        architecture = "全栈工程化项目（FastAPI 后端 + Vite/React 前端）"
    elif analysis.get("system_type") == "python_service":
        architecture = "Python 后端服务项目"

    backend = module_map.get("backend", {})
    frontend = module_map.get("frontend", {})
    routes = api_map.get("routes", [])
    relations = data_model_map.get("relations", [])

    lines: list[str] = []
    lines.append("# Architecture Report")
    lines.append("")
    lines.append("## 1. 系统总体定位")
    lines.append(f"- 项目路径：`{analysis.get('project_path')}`")
    lines.append(f"- 目标：{analysis.get('goal_text')}`" if False else f"- 目标：{analysis.get('goal_text')}")
    lines.append(f"- 系统类型：`{analysis.get('system_type')}`")
    lines.append(f"- 架构判断：{architecture}")
    lines.append("")

    lines.append("## 2. 后端架构")
    lines.append(f"- 运行入口：`{api_map.get('entry_file')}`")
    lines.append(f"- API 数量：{api_map.get('summary', {}).get('total_routes', 0)}")
    lines.append(f"- Service 文件数：{len(backend.get('service_files', []))}")
    lines.append(f"- Executor 文件数：{len(backend.get('executor_files', []))}")
    lines.append(f"- Verifier 文件数：{len(backend.get('verifier_files', []))}")
    lines.append(f"- Model 文件数：{len(backend.get('model_files', []))}")
    lines.append("")

    lines.append("### 后端关键特征")
    lines.append("- 当前接口集中在 `app/main.py`，属于单入口集中式 API 管理。")
    lines.append("- `services/` 是业务编排中心。")
    lines.append("- `executors/` 与 `verifiers/` 形成执行-校验双阶段机制。")
    lines.append("- `models/` + `alembic/` 说明数据层已具备迁移和实体抽象基础。")
    lines.append("")

    lines.append("## 3. 前端架构")
    lines.append(f"- 前端入口数量：{len(frontend.get('entrypoints', []))}")
    lines.append(f"- 组件数量：{len(frontend.get('component_files', []))}")
    lines.append(f"- API/Adapter 文件数量：{len(frontend.get('api_files', [])) + len(frontend.get('adapter_files', []))}")
    lines.append("")
    lines.append("### 前端关键特征")
    lines.append("- 前端以工作台面板结构组织。")
    lines.append("- 已存在 API client 与 adapter，说明前后端交互已开始分层。")
    lines.append("- 组件命名围绕 workspace / goal / outcome / executor 展开。")
    lines.append("")

    lines.append("## 4. 主业务链路")
    lines.append("1. 用户提交目标到 `/entry/submit`。")
    lines.append("2. 系统创建 `Goal` 和初始 `Outcome`。")
    lines.append("3. 用户执行 `/outcomes/{outcome_id}/execute`。")
    lines.append("4. 系统调用 executor 生成 artifact。")
    lines.append("5. verifier 执行校验并沉淀 verification。")
    lines.append("6. `/workspaces` 与 `/outcomes/{outcome_id}/timeline` 展示结果。")
    lines.append("")

    lines.append("## 5. 数据模型关系")
    lines.append(f"- 模型数量：{data_model_map.get('summary', {}).get('model_count', 0)}")
    lines.append(f"- 关系数量：{data_model_map.get('summary', {}).get('relation_count', 0)}")
    for rel in relations:
        lines.append(f"- `{rel['from_table']}.{rel['from_field']}` -> `{rel['to']}`")
    lines.append("")

    lines.append("## 6. 当前架构优势")
    lines.append("- 已形成从目标、执行、产物、验证到展示的完整闭环。")
    lines.append("- 已具备多层理解能力，可自动生成项目/模块/API/数据模型报告。")
    lines.append("- 执行与校验职责已拆分，为后续接入真实 Agent/Worker 奠定基础。")
    lines.append("")

    lines.append("## 7. 当前薄弱点")
    lines.append("- API 仍集中在 `app/main.py`，需要 router 化。")
    lines.append("- ORM relationship 尚未补齐。")
    lines.append("- 前后端接口映射尚未自动建立。")
    lines.append("- understanding 目前偏静态扫描，尚未做到更深层语义分析。")
    lines.append("")

    lines.append("## 8. 下一步建议")
    lines.append("- 拆分 API router。")
    lines.append("- 为模型补充 relationship。")
    lines.append("- 自动生成前后端接口映射表。")
    lines.append("- 接入更真实的执行器与分析器。")
    lines.append("")

    report_path = workspace / "architecture_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)
