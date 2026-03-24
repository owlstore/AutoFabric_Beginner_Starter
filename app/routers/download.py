"""Delivery package zip download."""
from __future__ import annotations

import io
import os
import zipfile

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.db.pool import get_conn
from app.errors import not_found

router = APIRouter(tags=["download"])


@router.get("/projects/{project_id}/delivery/download")
def download_delivery(project_id: int):
    """Stream the delivery package as a zip file."""
    # Find delivery dir from DB
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT delivery_dir FROM deliveries WHERE project_id = %s ORDER BY id DESC LIMIT 1",
            (project_id,),
        )
        row = cur.fetchone()
        cur.close()

    if not row or not row[0]:
        not_found("delivery", project_id)

    delivery_dir = row[0]
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
