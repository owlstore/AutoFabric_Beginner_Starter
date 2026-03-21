from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models
from app.routers.entry import router as entry_router
from app.routers.outcomes import router as outcomes_router
from app.routers.workspaces import router as workspaces_router
from app.routers.timeline import router as timeline_router
from app.routers.executions import router as executions_router
from app.routers.artifacts import router as artifacts_router
from app.routers.verifications import router as verifications_router

app = FastAPI(title="AutoFabric API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entry_router)
app.include_router(outcomes_router)
app.include_router(workspaces_router)
app.include_router(timeline_router)
app.include_router(executions_router)
app.include_router(artifacts_router)
app.include_router(verifications_router)


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "AutoFabric API",
        "version": "0.1.0",
    }
