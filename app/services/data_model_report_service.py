from __future__ import annotations

import json
from pathlib import Path


def build_data_model_report(workspace_dir: str) -> str:
    workspace = Path(workspace_dir)
    data_map_path = workspace / "data_model_map.json"
    data = json.loads(data_map_path.read_text(encoding="utf-8"))

    models = data.get("models", [])
    relations = data.get("relations", [])
    summary = data.get("summary", {})

    lines: list[str] = []
    lines.append("# Data Model Report")
    lines.append("")
    lines.append("## 1. 总体情况")
    lines.append(f"- 模型数量：{summary.get('model_count', 0)}")
    lines.append(f"- 关系数量：{summary.get('relation_count', 0)}")
    lines.append("")

    lines.append("## 2. 模型清单")
    for model in models:
        lines.append(f"### {model['class_name']} (`{model['table_name']}`)")
        lines.append(f"- 文件：`{model['file']}`")
        for field in model.get("fields", []):
            tags = []
            if field.get("primary_key"):
                tags.append("PK")
            if field.get("foreign_key"):
                tags.append(f"FK -> {field['foreign_key']}")
            tag_text = f" [{' | '.join(tags)}]" if tags else ""
            lines.append(f"- `{field['name']}`{tag_text}")
        lines.append("")

    lines.append("## 3. 关系清单")
    for rel in relations:
        lines.append(
            f"- `{rel['from_table']}.{rel['from_field']}` -> `{rel['to']}`"
        )
    lines.append("")

    lines.append("## 4. 数据结构结论")
    lines.append("- 当前系统以 `goals` 为起点，以 `outcomes` 为执行中心。")
    lines.append("- `executions`、`artifacts`、`verifications`、`flow_events` 都围绕 `outcomes` 展开。")
    lines.append("- 这是一种典型的“目标 -> 结果 -> 执行证据/验证证据/流转记录”结构。")
    lines.append("")

    lines.append("## 5. 下一步建议")
    lines.append("- 为模型增加 ORM relationship，提升查询与序列化便利性。")
    lines.append("- 输出实体关系图（ER 简图）。")
    lines.append("- 将前端展示字段与后端模型字段建立映射。")
    lines.append("")

    report = "\n".join(lines)
    report_path = workspace / "data_model_report.md"
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)
