from typing import Dict, Any
import httpx
from app.core.config import settings


def execute_openclaw_skill(skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    这里先保留成最小封装。
    如果你的本地 OpenClaw 暂时没有统一 HTTP API，先不要改它，
    只要把平台里的调用点收口到这里，后续你再替换为本地真实调用即可。
    """
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{settings.openclaw_base_url.rstrip('/')}/skills/{skill_name}",
                json=payload,
            )
            response.raise_for_status()
            return {"status": "success", "provider": "openclaw", "data": response.json()}
    except Exception as exc:
        return {
            "status": "pending_manual_integration",
            "provider": "openclaw",
            "error": str(exc),
            "note": "如果你本地 OpenClaw 不是这个接口形式，请把真实调用改到 app/services/openclaw_worker.py 里。",
        }
