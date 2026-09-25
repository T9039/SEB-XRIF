"""Feature importance route."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..model_store import get_store

router = APIRouter(tags=["analytics"])


@router.get("/importance")
def importance(
    source: str = Query("kalboard", description="Dataset source of the model."),
) -> dict:
    """Return native and SHAP feature importance for the source's model."""
    store = get_store(source)
    native = store.metadata.get("importance")
    shap = store.shap
    if not native and not shap:
        raise HTTPException(
            status_code=503,
            detail="No importance payload. Train a model with: "
            "uv run python -m analytics.train",
        )
    return {"source": source, "native": native, "shap": shap}
