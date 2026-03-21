from __future__ import annotations

import json
from pathlib import Path


def build_api_report(workspace_dir: str) -> str:
    workspace = Path(workspace_dir)
    api_map_path = workspace / "api_map.json"
    data = json.loads(api_map_path.read_text(encoding="utf-8"))

    routes = data.get("routes", [])
    summary = data.get("summary", {})

    lines: list[str] = []
    lines.append("# API Report")
    lines.append("")
    lines.append("## 1. 总体情况")
    lines.append(f"- 入口文件：`{data.get('entry_file')}`")
    lines.append(f"- 路由总数：{summary.get('total_routes', 0)}")
    lines.append(f"- GET 数量：{summary.get('methods', {}).get('GET', 0)}")
    lines.append(f"- POST 数量：{summary.get('methods', {}).get('POST', 0)}")
    lines.append("")

    lines.append("## 2. 路由清单")
    for route in routes:
        lines.append(
            f"- `{route['method']} {route['path']}` -> `{route['handler']}` "
            f"(`{route['file']}:{route['line']}`)"
        )
    lines.append("")

    lines.append("## 3. 接口层结论")
    lines.append("- 当前接口主要集中在 `app/main.py`，说明 API 还处于单入口集中式管理阶段。")
    lines.append("- 当前系统同时具备查询型接口和执行型接口。")
    lines.append("- `/entry/submit`、`/outcomes/.../execute`、`/outcomes/.../progress` 构成核心操作链。")
    lines.append("- `/workspaces` 与 `/outcomes/{outcome_id}/timeline` 构成核心展示链。")
    lines.append("")

    lines.append("## 4. 下一步建议")
    lines.append("- 将 `app/main.py` 中的接口逐步拆分到 router 模块。")
    lines.append("- 建立接口到 service 的映射表。")
    lines.append("- 梳理前端调用哪些后端接口。")
    lines.append("")

    report = "\n".join(lines)
    report_path = workspace / "api_report.md"
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)
