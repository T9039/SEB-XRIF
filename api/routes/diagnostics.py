"""Model diagnostics route (ROC, PR, calibration, learning curve)."""

from __future__ import annotations

import json
from dataclasses import replace

from fastapi import APIRouter, HTTPException, Query

from analytics.config import get_settings
from analytics.data import load_dataset
from analytics.diagnostics import compute_diagnostics

router = APIRouter(tags=["analytics"])


@router.get("/model/diagnostics")
def diagnostics(
    source: str = Query("kalboard", description="Dataset source of the model."),
) -> dict:
    """Compute out-of-fold diagnostic curves for the source's promoted model."""
    settings = get_settings()
    if source != settings.dataset:
        settings = replace(settings, dataset=source)
    model_path = settings.artifacts_for(source)[0]
    if not model_path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"No model artifact for source '{source}'. Train one with: "
            f"make train SOURCE={source}",
        )
    try:
        dataset = load_dataset(settings)
        payload = compute_diagnostics(settings, model_path=model_path, dataset=dataset)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return payload
