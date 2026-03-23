from __future__ import annotations

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    yield
    close_pool()


app = FastAPI(title="AutoFabric API", version="0.2.0", lifespan=lifespan)

# CORS — restrict to known origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
    ],
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


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "AutoFabric API",
        "version": "0.2.0",
    }
