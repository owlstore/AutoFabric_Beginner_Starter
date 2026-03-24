#!/usr/bin/env bash
set -euo pipefail

JOB_KEY="${JOB_KEY:-unknown}"
JOB_NAME="${JOB_NAME:-unknown}"
JOB_SELECTED_TOOL="${JOB_SELECTED_TOOL:-}"
PROTOTYPE_MODE="${PROTOTYPE_MODE:-default}"
PROTOTYPE_TARGET="${PROTOTYPE_TARGET:-page_structure}"
PROTOTYPE_COMPONENT_STYLE="${PROTOTYPE_COMPONENT_STYLE:-generic}"

OUT_JSON="runtime/executor_outputs/${JOB_KEY}.json"
OUT_DIR="frontend/src/components/autofabric"
META_DIR="runtime/generated_prototype/${JOB_KEY}"

mkdir -p "$OUT_DIR" "$META_DIR"

export JOB_KEY JOB_NAME JOB_SELECTED_TOOL PROTOTYPE_MODE PROTOTYPE_TARGET PROTOTYPE_COMPONENT_STYLE OUT_JSON OUT_DIR META_DIR

python3 - <<'PY'
import json
import os
import re
from pathlib import Path

job_key = os.environ.get("JOB_KEY", "unknown")
job_name = os.environ.get("JOB_NAME", "unknown")
selected_tool = os.environ.get("JOB_SELECTED_TOOL", "")
prototype_mode = os.environ.get("PROTOTYPE_MODE", "default")
prototype_target = os.environ.get("PROTOTYPE_TARGET", "page_structure")
prototype_style = os.environ.get("PROTOTYPE_COMPONENT_STYLE", "generic")
out_json = Path(os.environ["OUT_JSON"])
out_dir = Path(os.environ["OUT_DIR"])
meta_dir = Path(os.environ["META_DIR"])

def safe_component(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name)
    parts = [p.capitalize() for p in parts if p]
    return "".join(parts) or "GeneratedPrototype"


component = safe_component(job_name)
jsx_file = out_dir / f"Autofabric{component}.jsx"
meta_file = meta_dir / "prototype_meta.json"
generated_files = []

jsx_file.write_text(
f"""export default function Autofabric{component}() {{
  return (
    <section style={{{{
      padding: 18,
      border: "1px solid #dbe4ff",
      borderRadius: 16,
      background: "linear-gradient(180deg, #ffffff 0%, #f8fbff 100%)",
      boxShadow: "0 14px 30px rgba(15, 23, 42, 0.06)"
    }}}}>
      <div style={{{{ display: "flex", justifyContent: "space-between", gap: 12, marginBottom: 10 }}}}>
        <strong>{job_name}</strong>
        <span style={{{{ color: "#3b82f6", fontSize: 12 }}}}>{prototype_mode}</span>
      </div>
      <p style={{{{ margin: 0, color: "#475569", lineHeight: 1.6 }}}}>
        这是 AutoFabric 基于 {selected_tool or "默认工具"} 生成的原型占位组件，
        当前目标为 {prototype_target}，样式策略为 {prototype_style}。
      </p>
    </section>
  );
}}
""",
    encoding="utf-8",
)
generated_files.append(str(jsx_file))

extra_files = []
if prototype_mode in {"figma_sync", "figma_local_fallback"}:
    figma_spec = meta_dir / "figma_spec.json"
    figma_spec.write_text(
        json.dumps(
            {
                "job_key": job_key,
                "job_name": job_name,
                "selected_tool": selected_tool,
                "prototype_mode": prototype_mode,
                "frame_name": job_name,
                "sections": ["Hero", "Workspace", "Execution Timeline", "Delivery Summary"],
                "status": "token_ready" if prototype_mode == "figma_sync" else "local_fallback",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    extra_files.append(str(figma_spec))
elif prototype_mode == "react_vite":
    vite_notes = meta_dir / "vite_component_notes.md"
    vite_notes.write_text(
        f"""# React/Vite Prototype Notes

- job_key: {job_key}
- job_name: {job_name}
- selected_tool: {selected_tool}
- target: {prototype_target}

建议后续将该组件挂入 Vite 路由并接入页面级状态管理。
""",
        encoding="utf-8",
    )
    extra_files.append(str(vite_notes))

generated_files.extend(extra_files)

meta_file.write_text(
    json.dumps(
        {
            "job_key": job_key,
            "job_name": job_name,
            "selected_tool": selected_tool,
            "prototype_mode": prototype_mode,
            "prototype_target": prototype_target,
            "prototype_style": prototype_style,
            "generated_files": generated_files,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
generated_files.append(str(meta_file))

summary = "已生成原型说明/页面结构骨架"
if prototype_mode == "figma_sync":
    summary = "已生成 Figma 同步模式原型骨架"
elif prototype_mode == "figma_local_fallback":
    summary = "未接入 Figma Token，已生成本地原型骨架"
elif prototype_mode == "react_vite":
    summary = "已生成 React/Vite 原型组件骨架"

out_json.write_text(
    json.dumps(
        {
            "job_key": job_key,
            "executor": "prototype_agent",
            "job_name": job_name,
            "status": "completed",
            "summary": summary,
            "selected_tool": selected_tool,
            "prototype_mode": prototype_mode,
            "prototype_target": prototype_target,
            "prototype_style": prototype_style,
            "generated_file": str(jsx_file),
            "generated_files": generated_files,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

print(f"[prototype_agent] completed -> {job_key}")
for file_path in generated_files:
    print(f"[prototype_agent] generated -> {file_path}")
PY
