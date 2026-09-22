"""Model metrics route."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..model_store import get_store

router = APIRouter(tags=["analytics"])


@router.get("/metrics")
def metrics() -> dict:
    """Return the evaluation metrics recorded for the active model."""
    store = get_store()
    if not store.metadata:
        raise HTTPException(
            status_code=503,
            detail="No model metadata. Train one with: "
            "uv run python -m analytics.train",
        )
    return {
        "model": store.metadata.get("model"),
        "model_version": store.version,
        "created_utc": store.metadata.get("created_utc"),
        "metrics": store.metadata.get("metrics", {}),
    }
