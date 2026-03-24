"""Unified HTTP error helpers."""
from __future__ import annotations

from fastapi import HTTPException


def not_found(entity: str, entity_id: int | str):
    raise HTTPException(status_code=404, detail=f"{entity} {entity_id} not found")


def bad_request(msg: str):
    raise HTTPException(status_code=400, detail=msg)


def conflict(msg: str):
    raise HTTPException(status_code=409, detail=msg)
