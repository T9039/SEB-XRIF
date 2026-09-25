"""Prediction routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ..model_store import get_store
from ..schemas import PredictionResponse

router = APIRouter(tags=["prediction"])

_NOT_READY = "Model not loaded. Train one first with: uv run python -m analytics.train"


@router.post("/predict", response_model=PredictionResponse)
def predict(
    request: dict[str, Any],
    source: str = Query("kalboard", description="Dataset source of the model."),
) -> PredictionResponse:
    """Predict a support band for one learner using the source's model."""
    store = get_store(source)
    if not store.ready:
        raise HTTPException(status_code=503, detail=_NOT_READY)
    try:
        return PredictionResponse(**store.predict([request])[0])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/predict/batch", response_model=list[PredictionResponse])
def predict_batch(
    requests: list[dict[str, Any]],
    source: str = Query("kalboard", description="Dataset source of the model."),
) -> list[PredictionResponse]:
    """Vectorized prediction for a batch of learners."""
    store = get_store(source)
    if not store.ready:
        raise HTTPException(status_code=503, detail=_NOT_READY)
    try:
        return [PredictionResponse(**result) for result in store.predict(requests)]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
