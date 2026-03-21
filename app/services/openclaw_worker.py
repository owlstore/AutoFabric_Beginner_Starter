from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import os

import httpx

from app.core.config import settings


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _write_trace(skill_name: str, payload: dict[str, Any], response: dict[str, Any]) -> str:
    trace_dir = Path(".autofabric_runs/manual_openclaw_test")
    trace_dir.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in skill_name)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base = trace_dir / f"{stamp}_{safe_name}"

    request_path = base.with_suffix(".request.json")
    response_path = base.with_suffix(".response.json")

    request_path.write_text(
        json.dumps(
            {
                "skill_name": skill_name,
                "payload": payload,
                "written_at": _utc_now(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    response_path.write_text(
        json.dumps(response, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return str(response_path)


def execute_openclaw_skill(skill_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    兼容三种情况：
    1) OPENCLAW_MODE=http 且配置了 OPENCLAW_BASE_URL：按 HTTP 调用
    2) 其他情况：进入本地 bridge/placeholder 模式
    3) 无论哪种情况，都把调用收口在这里，不改平台主架构
    """
    mode = getattr(settings.executor, "openclaw_mode", None) or os.getenv("OPENCLAW_MODE", "bridge")
    base_url = os.getenv("OPENCLAW_BASE_URL", "").strip()

    if mode == "http" and base_url:
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{base_url.rstrip('/')}/skills/{skill_name}",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                result = {
                    "status": "success",
                    "provider": "openclaw",
                    "mode": "http",
                    "data": data,
                    "executed_at": _utc_now(),
                }
                trace_path = _write_trace(skill_name, payload, result)
                result["trace_path"] = trace_path
                return result
        except Exception as exc:
            result = {
                "status": "pending_manual_integration",
                "provider": "openclaw",
                "mode": "http",
                "error": str(exc),
                "note": "HTTP 模式已尝试，但当前 OpenClaw 接口未对齐；暂不改平台主线，只保留适配收口。",
                "executed_at": _utc_now(),
            }
            trace_path = _write_trace(skill_name, payload, result)
            result["trace_path"] = trace_path
            return result

    result = {
        "status": "accepted",
        "provider": "openclaw",
        "mode": "bridge_placeholder",
        "message": "OpenClaw bridge placeholder accepted the task.",
        "skill_name": skill_name,
        "received_payload": payload,
        "note": "当前先以本地桥接占位方式通过验证；后续再把真实 OpenClaw 调用接到这里。",
        "executed_at": _utc_now(),
    }
    trace_path = _write_trace(skill_name, payload, result)
    result["trace_path"] = trace_path
    return result
