from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT_DIR = Path(__file__).resolve().parents[2]
TOOL_RUN_DIR = ROOT_DIR / "runtime/tool_adapter_runs"
TOOL_RUN_DIR.mkdir(parents=True, exist_ok=True)


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat()


def _probe_python_module(module_name: str) -> bool:
    python_bin = shutil.which("python3") or shutil.which("python")
    if not python_bin:
        return False
    result = subprocess.run(
        [python_bin, "-c", f"import {module_name}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def adapter_probe(tool_key: str) -> Dict[str, Any]:
    notes: List[str] = []
    status = "ready"
    provider = ""

    if tool_key == "llm_workspace_tool":
        provider = "codex"
        model = os.getenv("LLM_MODEL") or os.getenv("LLM_REQUIREMENT_MODEL") or ""
        if model:
            notes.append(f"当前模型: {model}")
        else:
            notes.append("未显式配置模型，按系统默认模型运行")

    elif tool_key == "figma_adapter":
        provider = "figma"
        if os.getenv("FIGMA_TOKEN"):
            notes.append("检测到 FIGMA_TOKEN")
        else:
            status = "degraded"
            notes.append("未检测到 FIGMA_TOKEN，将以本地原型降级执行")

    elif tool_key == "react_vite_adapter":
        provider = "vite"
        if (ROOT_DIR / "frontend/package.json").exists():
            notes.append("检测到 frontend/package.json")
        else:
            status = "degraded"
            notes.append("未检测到前端 package.json")

    elif tool_key == "fastapi_adapter":
        provider = "fastapi"
        if (ROOT_DIR / "backend/app/main.py").exists():
            notes.append("检测到 backend/app/main.py")
        else:
            status = "degraded"
            notes.append("未检测到 FastAPI 主入口")

    elif tool_key == "postgres_adapter":
        provider = "postgresql"
        if (ROOT_DIR / "backend/app/core/database.py").exists():
            notes.append("检测到数据库配置模块")
        else:
            status = "degraded"
            notes.append("未检测到数据库配置模块")

    elif tool_key == "alembic_adapter":
        provider = "alembic"
        if (ROOT_DIR / "sql/migrations_v2").exists():
            notes.append("检测到 sql/migrations_v2")
        else:
            status = "degraded"
            notes.append("未检测到迁移目录")

    elif tool_key == "pytest_adapter":
        provider = "pytest"
        if _probe_python_module("pytest"):
            notes.append("pytest 可导入")
        else:
            status = "degraded"
            notes.append("pytest 未安装，将回退为 smoke test")

    elif tool_key == "playwright_adapter":
        provider = "playwright"
        if (ROOT_DIR / "frontend/package.json").exists():
            notes.append("存在前端工程，可继续接入 Playwright")
        else:
            status = "degraded"
            notes.append("未检测到前端工程，Playwright 适配器降级")

    elif tool_key == "openclaw_browser":
        provider = "openclaw"
        if (ROOT_DIR / "scripts/openclaw_bridge.sh").exists():
            notes.append("检测到 OpenClaw bridge 脚本")
        else:
            status = "degraded"
            notes.append("未检测到 OpenClaw bridge 脚本")

    elif tool_key == "docker_compose_adapter":
        provider = "docker"
        if shutil.which("docker"):
            notes.append("检测到 docker 命令")
        else:
            status = "degraded"
            notes.append("未检测到 docker 命令")

    elif tool_key == "github_actions_adapter":
        provider = "github"
        if (ROOT_DIR / ".git").exists():
            notes.append("检测到 Git 仓库")
        else:
            status = "degraded"
            notes.append("未检测到 Git 仓库")

    elif tool_key == "preview_runtime_adapter":
        provider = "autofabric"
        if (ROOT_DIR / "frontend").exists() and (ROOT_DIR / "backend").exists():
            notes.append("检测到前后端目录")
        else:
            status = "degraded"
            notes.append("未检测到完整前后端目录")

    else:
        provider = "unknown"
        status = "degraded"
        notes.append("未识别的 Tool Adapter")

    return {
        "tool_key": tool_key,
        "provider": provider,
        "status": status,
        "notes": notes,
        "checked_at": utc_now_iso(),
    }


def build_tool_receipt(
    *,
    job_key: str,
    job_name: str,
    agent_key: str,
    selected_tool: str,
    selected_tool_name: str,
    phase: str,
    execution_status: str,
    command: str,
    allowed_tools: List[str],
    skill_keys: List[str],
    policy_status: str,
    blocked_reasons: List[str],
    output_file: str = "",
    summary: str = "",
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    probe = adapter_probe(selected_tool) if selected_tool else {
        "tool_key": "",
        "provider": "",
        "status": "degraded",
        "notes": ["未选择 Tool Adapter"],
        "checked_at": utc_now_iso(),
    }

    return {
        "job_key": job_key,
        "job_name": job_name,
        "agent_key": agent_key,
        "selected_tool": selected_tool,
        "selected_tool_name": selected_tool_name or selected_tool,
        "allowed_tools": allowed_tools,
        "skill_keys": skill_keys,
        "phase": phase,
        "execution_status": execution_status,
        "policy_status": policy_status,
        "blocked_reasons": blocked_reasons,
        "command": command,
        "output_file": output_file,
        "summary": summary,
        "probe": probe,
        "updated_at": utc_now_iso(),
        "extra": extra or {},
    }


def write_tool_receipt(receipt: Dict[str, Any]) -> str:
    path = TOOL_RUN_DIR / f"{receipt['job_key']}.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
