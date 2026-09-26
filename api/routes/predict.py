"""Prediction routes."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from analytics.config import get_settings
from analytics.data import load_dataset

from ..model_store import get_store
from ..schemas import PredictionResponse

router = APIRouter(tags=["prediction"])

_NOT_READY = "Model not loaded. Train one first with: uv run python -m analytics.train"


@router.get("/model/features")
def model_features(
    source: str = Query("kalboard", description="Dataset source of the model."),
) -> dict:
    """Return the features (and option sets) a source's prediction expects."""
    settings = get_settings()
    if source != settings.dataset:
        settings = replace(settings, dataset=source)
    try:
        dataset = load_dataset(settings)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    options = {
        column: sorted(dataset.frame[column].dropna().astype(str).unique().tolist())[
            :50
        ]
        for column in dataset.categorical
    }
    return {
        "source": dataset.name,
        "target": dataset.target,
        "class_labels": dataset.class_labels,
        "features": dataset.features,
        "categorical": dataset.categorical,
        "numeric": dataset.numeric,
        "options": options,
    }


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
