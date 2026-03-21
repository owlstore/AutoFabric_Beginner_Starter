from __future__ import annotations

import json
from pathlib import Path


def build_module_report(workspace_dir: str) -> str:
    workspace = Path(workspace_dir)
    module_map_path = workspace / "module_map.json"
    data = json.loads(module_map_path.read_text(encoding="utf-8"))

    backend = data["backend"]
    frontend = data["frontend"]
    arch = data["architecture"]

    lines: list[str] = []
    lines.append("# Module Report")
    lines.append("")
    lines.append("## 1. 总体结构")
    lines.append(f"- 后端存在：{'是' if arch['backend_present'] else '否'}")
    lines.append(f"- 前端存在：{'是' if arch['frontend_present'] else '否'}")
    lines.append(f"- 迁移系统存在：{'是' if arch['migration_present'] else '否'}")
    lines.append(f"- 测试目录存在：{'是' if arch['tests_present'] else '否'}")
    lines.append("")

    lines.append("## 2. 后端入口")
    for item in backend["entrypoints"]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("## 3. 后端模块")
    lines.append(f"- API 文件数：{len(backend['api_files'])}")
    lines.append(f"- Schema 文件数：{len(backend['schema_files'])}")
    lines.append(f"- Service 文件数：{len(backend['service_files'])}")
    lines.append(f"- Executor 文件数：{len(backend['executor_files'])}")
    lines.append(f"- Verifier 文件数：{len(backend['verifier_files'])}")
    lines.append(f"- Model 文件数：{len(backend['model_files'])}")
    lines.append(f"- DB 文件数：{len(backend['db_files'])}")
    lines.append(f"- Core 文件数：{len(backend['core_files'])}")
    lines.append("")

    lines.append("### 关键 Service")
    for item in backend["service_files"][:12]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("### Executors")
    for item in backend["executor_files"]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("### Verifiers")
    for item in backend["verifier_files"]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("### Models")
    for item in backend["model_files"]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("## 4. 前端模块")
    lines.append("### 入口")
    for item in frontend["entrypoints"]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("### API / Adapter")
    for item in frontend["api_files"]:
        lines.append(f"- `{item}`")
    for item in frontend["adapter_files"]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("### Components")
    for item in frontend["component_files"][:20]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("## 5. 模块级结论")
    lines.append("- 当前项目已经形成后端、前端、执行器、验证器、服务编排、模型与数据库迁移的完整工程骨架。")
    lines.append("- `services/` 是当前系统最核心的业务编排层。")
    lines.append("- `executors/` 与 `verifiers/` 说明系统已经具备执行-校验双阶段机制。")
    lines.append("- `frontend/src/components/` 表明前端工作台已按面板化结构组织。")
    lines.append("")

    lines.append("## 6. 下一步建议")
    lines.append("- 继续识别 FastAPI 路由与接口清单。")
    lines.append("- 继续识别数据库实体关系。")
    lines.append("- 建立前后端接口映射表。")
    lines.append("- 输出正式架构图和逻辑流转图。")
    lines.append("")

    report = "\n".join(lines)
    report_path = workspace / "module_report.md"
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)