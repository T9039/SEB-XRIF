"""Advanced analytics routes: embeddings, cluster profiles, and PDP."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from analytics.config import get_settings
from analytics.embedding import compute_embedding
from analytics.pdp import compute_pdp

router = APIRouter(tags=["analytics"])


@router.get("/analytics/embedding")
def embedding(clusters: int = Query(3, ge=2, le=6)) -> dict:
    """PCA projection of learners plus KMeans cluster profiles."""
    return compute_embedding(get_settings(), n_clusters=clusters)


@router.get("/model/pdp")
def pdp(feature: str = Query(...), grid: int = Query(15, ge=5, le=40)) -> dict:
    """Average partial dependence for one numeric feature."""
    settings = get_settings()
    if not settings.model_path.exists():
        raise HTTPException(
            status_code=503, detail="No model artifact. Train one first."
        )
    try:
        return compute_pdp(feature, settings, grid_points=grid)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Bad feature: {exc}") from exc
