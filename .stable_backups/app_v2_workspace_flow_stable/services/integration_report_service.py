from __future__ import annotations

import json
from pathlib import Path


def build_integration_report(workspace_dir: str) -> str:
    workspace = Path(workspace_dir)
    data = json.loads((workspace / "integration_map.json").read_text(encoding="utf-8"))

    usage = data.get("frontend_usage", [])
    matched = data.get("matched_routes", [])
    summary = data.get("summary", {})

    lines: list[str] = []
    lines.append("# Frontend Backend Integration Report")
    lines.append("")
    lines.append("## 1. 总体情况")
    lines.append(f"- 扫描前端文件数：{data.get('frontend_files_scanned', 0)}")
    lines.append(f"- 含 HTTP 调用的文件数：{summary.get('files_with_http_calls', 0)}")
    lines.append(f"- 匹配到的后端路由数：{summary.get('matched_route_count', 0)}")
    lines.append("")

    lines.append("## 2. 前端调用情况")
    for item in usage:
        if not item.get("http_calls"):
            continue
        lines.append(f"### `{item['file']}`")
        for call in item.get("http_calls", []):
            lines.append(f"- 调用：`{call}`")
        lines.append("")

    lines.append("## 3. 已匹配到的接口")
    for item in matched:
        lines.append(f"- `{item['frontend_file']}` -> `{item['api_path']}` ({item['match_type']})")
    lines.append("")

    lines.append("## 4. 结论")
    if matched:
        lines.append("- 当前前端已经开始与后端接口形成明确对接。")
        lines.append("- `api/client.js` 与 `workspaceAdapter.js` 很可能是对接中枢。")
    else:
        lines.append("- 当前前端调用与后端路由尚未形成自动可识别的稳定映射。")
        lines.append("- 可能存在 base URL 拼接、封装调用或未统一抽象。")
    lines.append("")

    lines.append("## 5. 下一步建议")
    lines.append("- 统一前端 API 路径常量。")
    lines.append("- 为 adapter 层建立更明确的函数命名与接口映射。")
    lines.append("- 开始将 `app/main.py` 路由拆分到 router 模块。")
    lines.append("")

    path = workspace / "integration_report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
