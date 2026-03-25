from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.pool import open_pool, close_pool

# V2 routers (Manus system)
from app.routers.projects import router as projects_router
from app.routers.requirements import router as requirements_router
from app.routers.clarifications import router as clarifications_router
from app.routers.prototypes import router as prototypes_router
from app.routers.orchestration import router as orchestration_router
from app.routers.execution_runs import router as execution_runs_router
from app.routers.testing_runs import router as testing_runs_router
from app.routers.deliveries import router as deliveries_router
from app.routers.project_views import router as project_views_router
from app.routers.preview import router as preview_router
from app.routers.manus import router as manus_router
from app.routers.download import router as download_router
from app.routers.events import router as events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    yield
    close_pool()


app = FastAPI(title="AutoFabric API", version="0.2.0", lifespan=lifespan)

# CORS — allow localhost + Railway production domain
_cors_regex = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
_railway_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
if _railway_url:
    # Escape dots for regex and add HTTPS pattern
    _escaped = _railway_url.replace(".", r"\.")
    _cors_regex = rf"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^https://{_escaped}$"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=_cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects_router)
app.include_router(requirements_router)
app.include_router(clarifications_router)
app.include_router(prototypes_router)
app.include_router(orchestration_router)
app.include_router(execution_runs_router)
app.include_router(testing_runs_router)
app.include_router(deliveries_router)
app.include_router(project_views_router)
app.include_router(preview_router)
app.include_router(manus_router)
app.include_router(download_router)
app.include_router(events_router)


@app.get("/health")
def health():
    from app.config import config
    env_keys = [
        "DATABASE_URL", "POSTGRES_URL", "POSTGRES_HOST", "POSTGRES_DB",
        "POSTGRES_PASSWORD", "POSTGRES_PORT", "POSTGRES_USER",
        "LLM_PROVIDER", "OPENCLAW_BRIDGE_MODE", "PORT", "APP_PORT",
    ]
    return {
        "ok": True,
        "service": "AutoFabric API",
        "version": "0.2.0",
        "db_connected": True,
        "env_present": {k: bool(os.getenv(k)) for k in env_keys},
        "total_env_count": len(os.environ),
        "openclaw": {
            "enabled": True,
            "bridge_mode": config.openclaw.bridge_mode,
        },
    }
