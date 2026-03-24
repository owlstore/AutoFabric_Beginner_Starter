"""Delivery package zip download."""
from __future__ import annotations

import io
import os
import zipfile

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import config
from app.errors import not_found

router = APIRouter(tags=["download"])


@router.get("/projects/{project_id}/delivery/download")
def download_delivery(project_id: int):
    """Stream the delivery package as a zip file."""
    # Delivery files live under generated/project_{id}/delivery_package/
    # Fall back to the full project output dir if delivery_package doesn't exist
    base = os.path.join(config.openclaw.output_dir, f"project_{project_id}")
    delivery_dir = os.path.join(base, "delivery_package")

    if not os.path.isdir(delivery_dir):
        # Try the full project output as fallback
        delivery_dir = base

    if not os.path.isdir(delivery_dir):
        not_found("delivery directory", project_id)

    # Build zip in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(delivery_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                arcname = os.path.relpath(fpath, delivery_dir)
                zf.write(fpath, arcname)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="project_{project_id}_delivery.zip"',
        },
    )
