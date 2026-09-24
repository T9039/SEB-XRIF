"""Model diagnostics route (ROC, PR, calibration, learning curve)."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from analytics.config import get_settings
from analytics.diagnostics import compute_diagnostics

router = APIRouter(tags=["analytics"])


@router.get("/model/diagnostics")
def diagnostics() -> dict:
    """Compute out-of-fold diagnostic curves for the promoted model."""
    settings = get_settings()
    if not settings.model_path.exists():
        raise HTTPException(
            status_code=503,
            detail="No model artifact. Train one with: make train",
        )
    try:
        payload = compute_diagnostics(settings)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return payload
