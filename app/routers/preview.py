"""Serve generated prototype files for live preview."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from app.config import config

router = APIRouter(prefix="/preview", tags=["preview"])


def _proto_dir(project_id: int) -> Path:
    return Path(config.openclaw.output_dir) / f"project_{project_id}" / "prototype"


@router.get("/{project_id}")
def serve_preview_index(project_id: int):
    """Serve the prototype index.html for iframe embedding."""
    proto = _proto_dir(project_id)
    # Try built output first, then raw index.html
    for candidate in [proto / "dist" / "index.html", proto / "index.html"]:
        if candidate.exists():
            return FileResponse(candidate, media_type="text/html")
    raise HTTPException(404, detail=f"No prototype found for project {project_id}")


@router.get("/{project_id}/{file_path:path}")
def serve_preview_file(project_id: int, file_path: str):
    """Serve any file from the prototype directory."""
    proto = _proto_dir(project_id)
    # Try dist/ first (built output), then root
    for base in [proto / "dist", proto]:
        full = (base / file_path).resolve()
        # Prevent path traversal
        if not str(full).startswith(str(base.resolve())):
            raise HTTPException(403, detail="Access denied")
        if full.is_file():
            return FileResponse(full)
    raise HTTPException(404, detail=f"File not found: {file_path}")
