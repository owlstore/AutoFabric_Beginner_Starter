#!/usr/bin/env bash
set -euo pipefail

JOB_KEY="${JOB_KEY:-unknown}"
JOB_NAME="${JOB_NAME:-unknown}"

OUT_JSON="runtime/executor_outputs/${JOB_KEY}.json"
OUT_DIR="runtime/generated_build/${JOB_KEY}"
CODEX_REQ_DIR="runtime/codex_requests/${JOB_KEY}"
CODEX_RES_DIR="runtime/codex_results/${JOB_KEY}"

mkdir -p "$OUT_DIR" "$CODEX_REQ_DIR" "$CODEX_RES_DIR"
mkdir -p backend/app/services/autofabric_generated frontend/src/components/autofabric docs/autofabric runtime/generated_registry

python3 - <<'PY'
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

job_key = os.environ.get("JOB_KEY", "unknown")
job_name = os.environ.get("JOB_NAME", "unknown")
selected_tool = os.environ.get("JOB_SELECTED_TOOL", "")
adapter_mode = os.environ.get("TOOL_ADAPTER_MODE", "")
adapter_intent = os.environ.get("TOOL_ADAPTER_INTENT", "")
build_target_domain = os.environ.get("BUILD_TARGET_DOMAIN", "").strip()
build_target_kind = os.environ.get("BUILD_TARGET_KIND", "").strip()
build_target_hint = os.environ.get("BUILD_TARGET_HINT", "").strip()

out_dir = Path(f"runtime/generated_build/{job_key}")
codex_req_dir = Path(f"runtime/codex_requests/{job_key}")
codex_res_dir = Path(f"runtime/codex_results/{job_key}")
out_dir.mkdir(parents=True, exist_ok=True)
codex_req_dir.mkdir(parents=True, exist_ok=True)
codex_res_dir.mkdir(parents=True, exist_ok=True)

def slugify(text: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:80] or "task"

slug = slugify(job_name)
target_domain = "docs"
target_dir = Path("docs/autofabric")
target_type = "document"

if build_target_kind == "postgres":
    target_domain = "backend"
    target_dir = Path("sql/migrations_v2")
    target_type = "sql"
elif build_target_kind == "alembic":
    target_domain = "backend"
    target_dir = Path("sql/migrations_v2")
    target_type = "migration"
elif build_target_kind == "fastapi":
    target_domain = "backend"
    target_dir = Path("backend/app/services/autofabric_generated")
    target_type = "python"
elif build_target_domain in {"backend", "frontend", "docs"}:
    target_domain = build_target_domain
    if target_domain == "backend":
        target_dir = Path("backend/app/services/autofabric_generated")
        target_type = "python"
    elif target_domain == "frontend":
        target_dir = Path("frontend/src/components/autofabric")
        target_type = "jsx"
    else:
        target_dir = Path("docs/autofabric")
        target_type = "document"
elif any(k in job_name for k in ["接口", "API", "数据库", "模型", "迁移", "后端", "认证", "路由", "数据结构", "服务"]):
    target_domain = "backend"
    target_dir = Path("backend/app/services/autofabric_generated")
    target_type = "python"
elif any(k in job_name for k in ["前端", "页面", "原型", "UI", "组件", "工作台", "界面"]):
    target_domain = "frontend"
    target_dir = Path("frontend/src/components/autofabric")
    target_type = "jsx"

target_dir.mkdir(parents=True, exist_ok=True)

implementation_plan = out_dir / "implementation_plan.md"
implementation_meta = out_dir / "implementation_meta.json"
target_files_json = out_dir / "target_files.json"
prompt_file = codex_req_dir / "prompt.txt"
stdout_file = codex_res_dir / "stdout.txt"
stderr_file = codex_res_dir / "stderr.txt"
codex_meta_file = codex_res_dir / "result.json"
backend_codegen_stdout = out_dir / "backend_codegen_stdout.txt"
backend_codegen_stderr = out_dir / "backend_codegen_stderr.txt"
backend_codegen_result_file = out_dir / "backend_codegen_result.json"

prompt_file.write_text(
f"""你现在是 AutoFabric 的代码执行器。
任务：{job_name}

请输出中文实现建议，重点说明：
1. 应该新增哪些文件
2. 应该放在 backend/app/services 或 frontend/src/components 哪些位置
3. 如果涉及数据库，应如何组织 model / migration / schema
4. 如果涉及前端，应如何组织 page / hook / api / component
""",
encoding="utf-8"
)

codex_used = False
codex_status = "not_run"
codex_summary = "未检测到可用 Codex CLI，已回退到本地产物模式"

if shutil.which("codex"):
    codex_used = True
    proc = subprocess.run(["bash", "-lc", f"codex < '{prompt_file}'"], capture_output=True, text=True)
    stdout_file.write_text(proc.stdout or "", encoding="utf-8")
    stderr_file.write_text(proc.stderr or "", encoding="utf-8")
    if proc.returncode == 0:
        codex_status = "completed"
        codex_summary = "已通过 Codex CLI 生成结果"
    else:
        codex_status = "failed"
        codex_summary = "Codex CLI 调用失败，已回退到本地产物模式"
else:
    stderr_file.write_text("codex command not found", encoding="utf-8")

generated_files = []
backend_codegen_result = {}
backend_runtime_generated = False

if build_target_kind in {"fastapi", "postgres", "alembic"} and os.environ.get("JOB_PROJECT_ID"):
    helper_python = Path(".venv/bin/python")
    if not helper_python.exists():
        helper_python = Path(sys.executable)
    helper_env = os.environ.copy()
    helper_env["PYTHONPATH"] = os.getcwd() + (os.pathsep + helper_env["PYTHONPATH"] if helper_env.get("PYTHONPATH") else "")
    helper_proc = subprocess.run(
        [str(helper_python), "scripts/tool_adapters/backend_project_codegen.py"],
        capture_output=True,
        text=True,
        env=helper_env,
    )
    backend_codegen_stdout.write_text(helper_proc.stdout or "", encoding="utf-8")
    backend_codegen_stderr.write_text(helper_proc.stderr or "", encoding="utf-8")
    if helper_proc.returncode == 0:
        try:
            backend_codegen_result = json.loads(helper_proc.stdout or "{}")
        except Exception:
            backend_codegen_result = {"ok": False, "error": "helper returned invalid json"}
        if backend_codegen_result.get("ok"):
            backend_runtime_generated = True
            generated_files.extend(backend_codegen_result.get("generated_files") or [])
    else:
        backend_codegen_result = {
            "ok": False,
            "returncode": helper_proc.returncode,
            "stderr_file": str(backend_codegen_stderr),
        }
    backend_codegen_result_file.write_text(
        json.dumps(backend_codegen_result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
else:
    backend_codegen_stdout.write_text("", encoding="utf-8")
    backend_codegen_stderr.write_text("", encoding="utf-8")
    backend_codegen_result_file.write_text("{}", encoding="utf-8")

if build_target_kind == "postgres":
    sql_file = target_dir / f"autofabric_{slug}_schema.sql"
    sql_file.write_text(
f"""-- Auto-generated by AutoFabric postgres adapter
-- job_key: {job_key}
-- job_name: {job_name}
-- selected_tool: {selected_tool}
-- adapter_mode: {adapter_mode}

CREATE TABLE IF NOT EXISTS autofabric_{slug} (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    payload_json JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""",
        encoding="utf-8"
    )
    generated_files.append(str(sql_file))
elif build_target_kind == "alembic":
    sql_file = target_dir / f"autofabric_{slug}_migration.sql"
    sql_file.write_text(
f"""-- Auto-generated by AutoFabric alembic adapter
-- job_key: {job_key}
-- job_name: {job_name}
-- build_target_hint: {build_target_hint}

BEGIN;

-- TODO: replace placeholder DDL with real migration steps.
ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS autofabric_note TEXT;

COMMIT;
""",
        encoding="utf-8"
    )
    generated_files.append(str(sql_file))
elif target_domain == "backend":
    py_file = target_dir / f"autofabric_{slug}_service.py"
    py_file.write_text(
f'''"""
Auto-generated by AutoFabric build_executor
job_key: {job_key}
job_name: {job_name}
target_domain: backend
selected_tool: {selected_tool}
adapter_mode: {adapter_mode}
"""

from typing import Any, Dict

def run_{slug}() -> Dict[str, Any]:
    return {{
        "job_key": "{job_key}",
        "job_name": "{job_name}",
        "selected_tool": "{selected_tool}",
        "adapter_mode": "{adapter_mode}",
        "adapter_intent": "{adapter_intent}",
        "backend_runtime_generated": {str(backend_runtime_generated)},
        "backend_codegen_result_file": "{backend_codegen_result_file}",
        "message": "这是 AutoFabric 自动生成的后端服务封装文件，可继续接入真实业务实现。"
    }}
''',
        encoding="utf-8"
    )
    generated_files.append(str(py_file))
elif target_domain == "frontend":
    comp = "".join([p.capitalize() for p in re.split(r"[^A-Za-z0-9]+", slug) if p]) or "AutofabricComponent"
    jsx_file = target_dir / f"Autofabric{comp}.jsx"
    jsx_file.write_text(
f'''export default function Autofabric{comp}() {{
  return (
    <div style={{{{
      padding: 16,
      border: "1px solid #e5e7eb",
      borderRadius: 12,
      background: "#ffffff"
    }}}}>
      <h3 style={{{{ margin: 0, marginBottom: 8 }}}}>{job_name}</h3>
      <p style={{{{ margin: 0, color: "#6b7280" }}}}>
        这是 AutoFabric 自动生成的前端组件占位文件，可继续接入真实页面模块。
      </p>
      <p style={{{{ margin: "8px 0 0", color: "#94a3b8", fontSize: 12 }}}}>
        tool={selected_tool or "n/a"} · mode={adapter_mode or "default"}
      </p>
    </div>
  );
}}
''',
        encoding="utf-8"
    )
    generated_files.append(str(jsx_file))
else:
    md_file = target_dir / f"autofabric_{slug}.md"
    md_file.write_text(
f"""# {job_name}

- job_key: {job_key}
- target_domain: docs

这是 AutoFabric 自动生成的文档型占位产物。
""",
        encoding="utf-8"
    )
    generated_files.append(str(md_file))

implementation_plan.write_text(
f"""# Implementation Plan

## Job
- key: {job_key}
- name: {job_name}

## Target Domain
- domain: {target_domain}
- type: {target_type}
- output_dir: {target_dir}
- selected_tool: {selected_tool or "-"}
- adapter_mode: {adapter_mode or "-"}
- adapter_intent: {adapter_intent or "-"}
- build_target_kind: {build_target_kind or "-"}
- build_target_hint: {build_target_hint or "-"}
- backend_runtime_generated: {backend_runtime_generated}
- backend_codegen_result: {backend_codegen_result_file}

## Generated Files
{chr(10).join(f"- {x}" for x in generated_files)}

## Codex
- used: {codex_used}
- status: {codex_status}
- prompt: {prompt_file}
- stdout: {stdout_file}
- stderr: {stderr_file}
""",
encoding="utf-8"
)

meta = {
    "job_key": job_key,
    "job_name": job_name,
    "target_domain": target_domain,
    "target_type": target_type,
    "output_dir": str(target_dir),
    "selected_tool": selected_tool,
    "adapter_mode": adapter_mode,
    "adapter_intent": adapter_intent,
    "build_target_kind": build_target_kind,
    "build_target_hint": build_target_hint,
    "backend_runtime_generated": backend_runtime_generated,
    "backend_codegen_result": backend_codegen_result,
    "generated_files": generated_files,
    "codex_used": codex_used,
    "codex_status": codex_status,
    "summary": "已将 build_agent 产物写回正式工程产物目录"
}
implementation_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
target_files_json.write_text(json.dumps({"files": generated_files}, ensure_ascii=False, indent=2), encoding="utf-8")
codex_meta_file.write_text(
    json.dumps(
        {
            "job_key": job_key,
            "job_name": job_name,
            "codex_used": codex_used,
            "codex_status": codex_status,
            "summary": codex_summary,
            "prompt_file": str(prompt_file),
            "stdout_file": str(stdout_file),
            "stderr_file": str(stderr_file),
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8"
)

Path(f"runtime/executor_outputs/{job_key}.json").write_text(
    json.dumps(
        {
            "job_key": job_key,
            "executor": "build_agent",
            "job_name": job_name,
            "status": "completed",
            "summary": codex_summary if codex_used else "已将构建产物写回正式工程产物目录",
            "artifact_dir": str(out_dir),
            "target_domain": target_domain,
            "selected_tool": selected_tool,
            "adapter_mode": adapter_mode,
            "adapter_intent": adapter_intent,
            "build_target_kind": build_target_kind,
            "backend_runtime_generated": backend_runtime_generated,
            "backend_codegen_result_file": str(backend_codegen_result_file),
            "backend_codegen_result": backend_codegen_result,
            "target_output_dir": str(target_dir),
            "artifact_files": [
                str(implementation_plan),
                str(implementation_meta),
                str(target_files_json),
                str(codex_meta_file),
                str(backend_codegen_stdout),
                str(backend_codegen_stderr),
                str(backend_codegen_result_file),
                *generated_files
            ]
        },
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)
print(f"[build_agent] completed -> {job_key}")
for f in generated_files:
    print(f"[build_agent] generated -> {f}")
PY

python3 scripts/rebuild_autofabric_indexes.py >/dev/null 2>&1 || true
python3 scripts/rebuild_autofabric_showcase.py >/dev/null 2>&1 || true
