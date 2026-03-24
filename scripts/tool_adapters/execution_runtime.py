from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict

from tool_adapters.runtime_contract import adapter_probe


ROOT_DIR = Path(__file__).resolve().parents[2]
EXECUTOR_OUTPUT_DIR = ROOT_DIR / "runtime/executor_outputs"


def _bool_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        return ""
    return "true" if str(value).strip().lower() in {"1", "true", "yes", "on"} else "false"


def _base_adapter_info(tool_key: str, script_rel: str) -> Dict[str, Any]:
    probe = adapter_probe(tool_key) if tool_key else {
        "tool_key": "",
        "provider": "",
        "status": "degraded",
        "notes": ["未选择 Tool Adapter"],
        "checked_at": "",
    }
    return {
        "tool_key": tool_key,
        "script_rel": script_rel,
        "probe": probe,
        "provider": probe.get("provider") or "",
        "probe_status": probe.get("status") or "",
        "probe_notes": probe.get("notes") or [],
        "fallback_used": probe.get("status") == "degraded",
        "mode": "default",
        "intent": "",
        "command": f"bash {script_rel}",
        "env_overrides": {
            "TOOL_ADAPTER_KEY": tool_key,
            "TOOL_ADAPTER_PROVIDER": probe.get("provider") or "",
            "TOOL_ADAPTER_PROBE_STATUS": probe.get("status") or "",
        },
    }


def resolve_tool_execution(tool_key: str, script_rel: str, runtime_job: Dict[str, Any]) -> Dict[str, Any]:
    info = _base_adapter_info(tool_key, script_rel)
    job_name = str(runtime_job.get("job_name") or "")

    if tool_key == "llm_workspace_tool":
        info["mode"] = "llm_workspace"
        info["intent"] = "基于 Codex 工作区执行需求/规划类任务"

    elif tool_key == "figma_adapter":
        has_token = bool(os.getenv("FIGMA_TOKEN"))
        info["mode"] = "figma_sync" if has_token else "figma_local_fallback"
        info["intent"] = "生成原型说明并尝试同步设计语义"
        info["command"] = (
            "bash scripts/executors/prototype_executor.sh --figma-sync"
            if has_token
            else "bash scripts/executors/prototype_executor.sh --local-prototype"
        )
        info["env_overrides"].update(
            {
                "PROTOTYPE_MODE": info["mode"],
                "PROTOTYPE_TARGET": "design_spec",
                "PROTOTYPE_COMPONENT_STYLE": "figma",
            }
        )

    elif tool_key == "react_vite_adapter":
        info["mode"] = "react_vite"
        info["intent"] = "输出可进入 Vite 工程的 React 页面骨架"
        info["command"] = "bash scripts/executors/prototype_executor.sh --react-vite"
        info["env_overrides"].update(
            {
                "PROTOTYPE_MODE": "react_vite",
                "PROTOTYPE_TARGET": "frontend_component",
                "PROTOTYPE_COMPONENT_STYLE": "vite",
            }
        )

    elif tool_key == "fastapi_adapter":
        info["mode"] = "fastapi_backend"
        info["intent"] = "生成 FastAPI 路由与服务层骨架"
        info["command"] = "bash scripts/executors/build_executor.sh --fastapi"
        info["env_overrides"].update(
            {
                "BUILD_TARGET_DOMAIN": "backend",
                "BUILD_TARGET_KIND": "fastapi",
                "BUILD_TARGET_HINT": "api_router",
            }
        )

    elif tool_key == "postgres_adapter":
        info["mode"] = "postgres_schema"
        info["intent"] = "生成数据库模型与表结构说明"
        info["command"] = "bash scripts/executors/build_executor.sh --postgres"
        info["env_overrides"].update(
            {
                "BUILD_TARGET_DOMAIN": "backend",
                "BUILD_TARGET_KIND": "postgres",
                "BUILD_TARGET_HINT": "db_schema",
            }
        )

    elif tool_key == "alembic_adapter":
        info["mode"] = "alembic_migration"
        info["intent"] = "生成迁移与演进说明骨架"
        info["command"] = "bash scripts/executors/build_executor.sh --alembic"
        info["env_overrides"].update(
            {
                "BUILD_TARGET_DOMAIN": "backend",
                "BUILD_TARGET_KIND": "alembic",
                "BUILD_TARGET_HINT": "migration_plan",
            }
        )

    elif tool_key == "pytest_adapter":
        info["mode"] = "pytest"
        info["intent"] = "优先执行 pytest，用 smoke test 兜底"
        info["command"] = "bash scripts/executors/testing_executor.sh --pytest"
        info["env_overrides"].update(
            {
                "TEST_EXECUTION_MODE": "pytest",
                "TEST_TARGET_SCOPE": "backend",
            }
        )

    elif tool_key == "playwright_adapter":
        info["mode"] = "playwright"
        info["intent"] = "验证前端可构建性，并为 E2E 浏览器测试预留入口"
        info["command"] = "bash scripts/executors/testing_executor.sh --playwright"
        info["env_overrides"].update(
            {
                "TEST_EXECUTION_MODE": "playwright",
                "TEST_TARGET_SCOPE": "frontend",
            }
        )

    elif tool_key == "openclaw_browser":
        info["mode"] = "openclaw_browser"
        info["intent"] = "通过 OpenClaw 浏览器执行器生成浏览器动作记录"
        info["command"] = "bash scripts/executors/browser_executor.sh --openclaw-browser"
        info["env_overrides"].update(
            {
                "BROWSER_EXECUTION_MODE": "openclaw_browser",
            }
        )

    elif tool_key == "docker_compose_adapter":
        info["mode"] = "docker_compose"
        info["intent"] = "输出 docker compose 部署骨架"
        info["command"] = "bash scripts/executors/delivery_executor.sh --docker-compose"
        info["env_overrides"].update(
            {
                "DELIVERY_EXECUTION_MODE": "docker_compose",
                "DELIVERY_TARGET": "deployment_bundle",
            }
        )

    elif tool_key == "github_actions_adapter":
        info["mode"] = "github_actions"
        info["intent"] = "输出 CI/CD workflow 骨架"
        info["command"] = "bash scripts/executors/delivery_executor.sh --github-actions"
        info["env_overrides"].update(
            {
                "DELIVERY_EXECUTION_MODE": "github_actions",
                "DELIVERY_TARGET": "ci_bundle",
            }
        )

    elif tool_key == "preview_runtime_adapter":
        info["mode"] = "preview_runtime"
        info["intent"] = "输出预览运行时说明与交付入口"
        info["command"] = "bash scripts/executors/delivery_executor.sh --preview-runtime"
        info["env_overrides"].update(
            {
                "DELIVERY_EXECUTION_MODE": "preview_runtime",
                "DELIVERY_TARGET": "preview_bundle",
            }
        )

    else:
        info["mode"] = "fallback_executor"
        info["intent"] = f"未识别 Tool Adapter，回退到默认执行器: {job_name}"

    info["env_overrides"]["TOOL_ADAPTER_MODE"] = info["mode"]
    info["env_overrides"]["TOOL_ADAPTER_INTENT"] = info["intent"]
    info["env_overrides"]["TOOL_ADAPTER_FALLBACK_USED"] = "true" if info["fallback_used"] else "false"
    return info


def _load_executor_output(output_path: Path) -> Dict[str, Any]:
    if not output_path.exists():
        return {}
    try:
        return json.loads(output_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_executor_output(output_path: Path, payload: Dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def execute_tool_job(
    *,
    root_dir: Path,
    runtime_job: Dict[str, Any],
    request_payload: Dict[str, Any],
    script_rel: str,
) -> Dict[str, Any]:
    tool_key = str(runtime_job.get("selected_tool") or "")
    job_key = str(runtime_job.get("job_key") or "")
    output_path = EXECUTOR_OUTPUT_DIR / f"{job_key}.json"
    adapter = resolve_tool_execution(tool_key, script_rel, runtime_job)

    child_env = os.environ.copy()
    child_env.update(
        {
            "JOB_KEY": job_key,
            "JOB_NAME": str(runtime_job.get("job_name") or ""),
            "JOB_EXECUTOR": str(runtime_job.get("executor") or ""),
            "JOB_AGENT_KEY": str(runtime_job.get("agent_key") or runtime_job.get("executor") or ""),
            "JOB_PROJECT_ID": str(request_payload.get("project_id") or ""),
            "JOB_DISPATCH_ID": str(request_payload.get("dispatch_id") or ""),
            "JOB_REQUIRED_SKILLS_JSON": json.dumps(runtime_job.get("required_skills") or [], ensure_ascii=False),
            "JOB_ALLOWED_TOOLS_JSON": json.dumps(runtime_job.get("allowed_tools") or [], ensure_ascii=False),
            "JOB_SELECTED_TOOL": tool_key,
            "JOB_SELECTED_TOOL_NAME": str(runtime_job.get("selected_tool_name") or ""),
        }
    )
    child_env.update(adapter.get("env_overrides") or {})

    completed = subprocess.run(
        ["bash", script_rel],
        cwd=str(root_dir),
        env=child_env,
        capture_output=True,
        text=True,
    )

    output_payload = _load_executor_output(output_path)
    adapter_result = {
        "tool_key": adapter.get("tool_key") or tool_key,
        "provider": adapter.get("provider") or "",
        "mode": adapter.get("mode") or "",
        "intent": adapter.get("intent") or "",
        "command": adapter.get("command") or f"bash {script_rel}",
        "probe_status": adapter.get("probe_status") or "",
        "probe_notes": adapter.get("probe_notes") or [],
        "fallback_used": bool(adapter.get("fallback_used")),
        "script_rel": script_rel,
        "returncode": int(completed.returncode),
    }
    if output_payload:
        output_payload["tool_adapter"] = adapter_result
        _write_executor_output(output_path, output_payload)

    return {
        "completed": completed,
        "adapter": adapter_result,
        "output_payload": output_payload,
        "stdout": completed.stdout or "",
        "stderr": completed.stderr or "",
        "output_file": str(output_path),
    }

