"""Artifact loading and inference for the API.

The promoted pipeline and its metadata are loaded once at startup. If no
artifact exists yet, the service still starts and reports a degraded state;
prediction routes return HTTP 503 until a model is trained.
"""

from __future__ import annotations

import json
from typing import Any

import joblib
import pandas as pd

from .config import get_api_settings


class ModelStore:
    """Holds the loaded pipeline, metadata, and explanation payloads."""

    def __init__(self) -> None:
        self.pipeline: Any | None = None
        self.metadata: dict[str, Any] = {}
        self.shap: dict[str, Any] = {}

    def load(self) -> ModelStore:
        settings = get_api_settings()
        if settings.model_path.exists():
            self.pipeline = joblib.load(settings.model_path)
        if settings.metadata_path.exists():
            self.metadata = json.loads(
                settings.metadata_path.read_text(encoding="utf-8")
            )
        if settings.shap_path.exists():
            self.shap = json.loads(settings.shap_path.read_text(encoding="utf-8"))
        return self

    @property
    def ready(self) -> bool:
        return self.pipeline is not None

    @property
    def version(self) -> str:
        return str(self.metadata.get("model_version", "unset"))

    @property
    def feature_order(self) -> list[str]:
        order = self.metadata.get("feature_order")
        if order:
            return list(order)
        return list(self.metadata.get("metrics", {}).get("features", [])) or []

    def predict(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Predict a tier and per-class probabilities for each input row."""
        if self.pipeline is None:
            raise RuntimeError("model not loaded")

        frame = pd.DataFrame(rows)
        order = self.feature_order
        if order:
            frame = frame[order]

        predictions = self.pipeline.predict(frame)
        if hasattr(self.pipeline, "predict_proba"):
            probabilities = self.pipeline.predict_proba(frame)
            classes = list(self.pipeline.named_steps["clf"].classes_)
        else:  # pragma: no cover - all catalog models expose predict_proba
            probabilities = [
                [1.0 if p == pred else 0.0 for p in predictions] for pred in predictions
            ]
            classes = sorted(set(predictions))

        results: list[dict[str, Any]] = []
        for index, label in enumerate(predictions):
            row = {
                str(c): float(probabilities[index][j]) for j, c in enumerate(classes)
            }
            results.append(
                {
                    "prediction": str(label),
                    "probabilities": row,
                    "confidence": float(max(row.values())),
                }
            )
        return results


_store = ModelStore()


def get_store() -> ModelStore:
    """Return the process-wide model store."""
    return _store
