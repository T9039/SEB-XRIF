"""Prediction routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..model_store import get_store
from ..schemas import PredictionRequest, PredictionResponse

router = APIRouter(tags=["prediction"])

_NOT_READY = "Model not loaded. Train one first with: uv run python -m analytics.train"


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    """Predict the performance tier for a single learner."""
    store = get_store()
    if not store.ready:
        raise HTTPException(status_code=503, detail=_NOT_READY)
    return PredictionResponse(**store.predict([request.model_dump()])[0])


@router.post("/predict/batch", response_model=list[PredictionResponse])
def predict_batch(requests: list[PredictionRequest]) -> list[PredictionResponse]:
    """Vectorized tier prediction for a batch of learners."""
    store = get_store()
    if not store.ready:
        raise HTTPException(status_code=503, detail=_NOT_READY)
    rows = [request.model_dump() for request in requests]
    return [PredictionResponse(**result) for result in store.predict(rows)]
