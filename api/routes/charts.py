"""Saved Chart Studio views, persisted in Postgres."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from analytics.db import delete_view, get_engine, list_views, save_view

router = APIRouter(tags=["studio"])


class ChartViewRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    spec: dict[str, Any]


@router.get("/charts")
def charts() -> list[dict]:
    """List all saved chart views."""
    return list_views(get_engine())


@router.post("/charts")
def create_chart(request: ChartViewRequest) -> dict:
    """Insert or update a saved chart view."""
    return save_view(get_engine(), request.name, request.spec)


@router.delete("/charts/{name}")
def remove_chart(name: str) -> dict:
    """Delete a saved chart view by name."""
    if not delete_view(get_engine(), name):
        raise HTTPException(status_code=404, detail=f"No saved view named {name}")
    return {"deleted": name}
