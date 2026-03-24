"""Stage 3: Prototype Designer — LLM generates IA, page flow, and React UI code."""
from __future__ import annotations

import json
import os
from pathlib import Path

from app.llm import get_llm

IA_PROMPT = """\
你是一名资深 UX 架构师。基于需求卡，设计完整的信息架构。

输出 JSON：
{
  "pages": [
    {"name": "页面名", "purpose": "用途", "key_components": ["组件1", "组件2"]},
    ...
  ],
  "navigation": {
    "type": "sidebar|tabs|top_nav|bottom_nav",
    "structure": [{"label": "导航项", "page": "页面名", "icon": "图标名"}]
  },
  "user_flows": [
    {"name": "流程名", "steps": ["步骤1 → 步骤2 → ..."]}
  ]
}"""

MODULE_PROMPT = """\
你是一名系统架构师。基于信息架构，设计模块依赖和 API。同时生成 Mermaid 架构图。

输出 JSON：
{
  "module_map": [
    {"name": "模块名", "responsibilities": ["职责1"], "depends_on": ["依赖模块"]}
  ],
  "api_design": [
    {"method": "GET|POST|PUT|DELETE", "path": "/api/...", "description": "描述", "request_body": "可选", "response": "描述"}
  ],
  "mermaid_architecture": "graph TD\\n  A[模块A] --> B[模块B]\\n  ...",
  "mermaid_er": "erDiagram\\n  User ||--o{ Order : places\\n  ..."
}"""

UI_PROTOTYPE_PROMPT = """\
你是一名资深前端工程师和 UI 设计师。基于信息架构和模块设计，为每个页面生成完整的 React + Tailwind CSS 组件代码。

要求：
1. 使用 React 函数组件 + Tailwind CSS
2. 包含真实感的 mock 数据（不要 lorem ipsum）
3. 响应式设计（mobile-first）
4. 现代设计语言：圆角(rounded-xl)、柔和阴影、渐变色、微动画(transition)
5. 暗色主题（bg-gray-900 系）
6. 包含完整的页面布局、导航、表单、列表、卡片、表格等
7. 每个文件可独立渲染
8. 使用 Lucide React 图标（import { Icon } from 'lucide-react'）

输出 JSON：
{
  "files": [
    {"path": "src/App.jsx", "content": "完整代码"},
    {"path": "src/pages/Dashboard.jsx", "content": "完整代码"},
    {"path": "src/components/Sidebar.jsx", "content": "完整代码"},
    ...
  ],
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "tailwindcss": "^3.4.0",
    "lucide-react": "^0.400.0"
  }
}"""


def design_ia(requirement_card: dict) -> dict:
    """Generate information architecture from requirement card."""
    llm = get_llm()
    return llm.complete_json(
        system=IA_PROMPT,
        user=f"需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}",
        tier="strong",
        max_tokens=2048,
    )


def design_modules(requirement_card: dict, ia: dict) -> dict:
    """Generate module map, API design, and Mermaid diagrams."""
    llm = get_llm()
    user_msg = (
        f"需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}\n\n"
        f"信息架构：\n{json.dumps(ia, ensure_ascii=False, indent=2)}"
    )
    return llm.complete_json(
        system=MODULE_PROMPT,
        user=user_msg,
        tier="strong",
        max_tokens=3000,
    )


def generate_ui_prototype(requirement_card: dict, ia: dict, modules: dict) -> dict:
    """Generate React + Tailwind UI prototype code."""
    llm = get_llm()
    user_msg = (
        f"需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}\n\n"
        f"信息架构：\n{json.dumps(ia, ensure_ascii=False, indent=2)}\n\n"
        f"模块设计：\n{json.dumps(modules, ensure_ascii=False, indent=2)}"
    )
    return llm.complete_json(
        system=UI_PROTOTYPE_PROMPT,
        user=user_msg,
        tier="strong",
        max_tokens=8000,
    )


def write_prototype_files(project_id: int, prototype_data: dict) -> str:
    """Write generated prototype files to disk and return the output directory."""
    output_dir = os.getenv("OPENCLAW_OUTPUT_DIR", "generated")
    proto_dir = Path(output_dir) / f"project_{project_id}" / "prototype"
    proto_dir.mkdir(parents=True, exist_ok=True)

    # Write source files
    for file_info in prototype_data.get("files", []):
        file_path = proto_dir / file_info["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file_info["content"], encoding="utf-8")

    # Write package.json
    deps = prototype_data.get("dependencies", {})
    pkg = {
        "name": f"autofabric-prototype-{project_id}",
        "private": True,
        "version": "0.1.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
        },
        "dependencies": deps,
        "devDependencies": {
            "@vitejs/plugin-react": "^4.3.0",
            "vite": "^5.4.0",
            "autoprefixer": "^10.4.0",
            "postcss": "^8.4.0",
        },
    }
    (proto_dir / "package.json").write_text(
        json.dumps(pkg, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Write vite.config.js
    (proto_dir / "vite.config.js").write_text(
        'import { defineConfig } from "vite";\n'
        'import react from "@vitejs/plugin-react";\n\n'
        "export default defineConfig({\n"
        "  plugins: [react()],\n"
        "});\n",
        encoding="utf-8",
    )

    # Write index.html
    (proto_dir / "index.html").write_text(
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        '  <meta charset="UTF-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        f"  <title>AutoFabric Prototype #{project_id}</title>\n"
        '</head>\n<body>\n  <div id="root"></div>\n'
        '  <script type="module" src="/src/main.jsx"></script>\n'
        "</body>\n</html>\n",
        encoding="utf-8",
    )

    # Write main.jsx if not in files
    main_exists = any(f["path"] == "src/main.jsx" for f in prototype_data.get("files", []))
    if not main_exists:
        main_jsx = proto_dir / "src" / "main.jsx"
        main_jsx.parent.mkdir(parents=True, exist_ok=True)
        main_jsx.write_text(
            'import React from "react";\n'
            'import ReactDOM from "react-dom/client";\n'
            'import App from "./App";\n'
            'import "./index.css";\n\n'
            'ReactDOM.createRoot(document.getElementById("root")).render(\n'
            "  <React.StrictMode><App /></React.StrictMode>\n"
            ");\n",
            encoding="utf-8",
        )

    # Write minimal index.css with Tailwind directives
    css_path = proto_dir / "src" / "index.css"
    if not css_path.exists():
        css_path.write_text(
            "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n",
            encoding="utf-8",
        )

    # Write tailwind.config.js
    (proto_dir / "tailwind.config.js").write_text(
        "/** @type {import('tailwindcss').Config} */\n"
        "export default {\n"
        '  content: ["./index.html", "./src/**/*.{js,jsx}"],\n'
        "  theme: { extend: {} },\n"
        "  plugins: [],\n"
        "};\n",
        encoding="utf-8",
    )

    # Write postcss.config.js
    (proto_dir / "postcss.config.js").write_text(
        "export default {\n"
        "  plugins: {\n"
        "    tailwindcss: {},\n"
        "    autoprefixer: {},\n"
        "  },\n"
        "};\n",
        encoding="utf-8",
    )

    # Auto-build: try npm install + build for preview serving
    _try_build(proto_dir)

    return str(proto_dir)


def _try_build(proto_dir: Path) -> bool:
    """Best-effort: run npm install + build. Returns True on success."""
    import subprocess
    import shutil

    npm = shutil.which("npm")
    if not npm:
        return False

    try:
        subprocess.run(
            [npm, "install"],
            cwd=str(proto_dir),
            timeout=60,
            capture_output=True,
        )
        result = subprocess.run(
            [npm, "run", "build"],
            cwd=str(proto_dir),
            timeout=60,
            capture_output=True,
        )
        return result.returncode == 0
    except Exception:
        return False
