"""Artifact loading and inference for the API.

Loads the promoted pipeline and metadata once at startup, either from the local
joblib artifact or the MLflow model registry (``model_source``). If no model
exists the service still starts and reports a degraded state; prediction routes
return HTTP 503 until a model is available.
"""

from __future__ import annotations

import json
from typing import Any

import joblib
import pandas as pd

from analytics.config import get_settings as get_analytics_settings
from analytics.decision import apply_thresholds, support_band

from .config import ApiSettings, get_api_settings
from .logging import get_logger

logger = get_logger("api.model_store")


class ModelStore:
    """Holds the loaded pipeline, metadata, and explanation payloads."""

    def __init__(self) -> None:
        self.pipeline: Any | None = None
        self.metadata: dict[str, Any] = {}
        self.shap: dict[str, Any] = {}
        self.support_bands: dict[str, str] = {}
        self.decision_thresholds: dict[str, float] = {}

    def load(self) -> ModelStore:
        """Load the pipeline and sidecars from the configured source."""
        settings = get_api_settings()

        analytics = get_analytics_settings()
        self.support_bands = dict(analytics.support_bands)
        self.decision_thresholds = dict(analytics.decision_thresholds)

        if settings.model_source == "registry":
            self._load_from_registry(settings)
        if self.pipeline is None and settings.model_path.exists():
            self.pipeline = joblib.load(settings.model_path)
            logger.info("model_loaded", source="local", path=str(settings.model_path))

        if settings.metadata_path.exists():
            self.metadata = json.loads(
                settings.metadata_path.read_text(encoding="utf-8")
            )
        if settings.run_path.exists():
            run = json.loads(settings.run_path.read_text(encoding="utf-8"))
            self.metadata = {**self.metadata, **run}
        if settings.shap_path.exists():
            self.shap = json.loads(settings.shap_path.read_text(encoding="utf-8"))
        return self

    def _load_from_registry(self, settings: ApiSettings) -> None:
        """Best-effort load of the latest registered model version."""
        try:
            import mlflow

            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            uri = f"models:/{settings.registered_model}/latest"
            self.pipeline = mlflow.sklearn.load_model(uri)
            logger.info("model_loaded", source="registry", uri=uri)
        except Exception as exc:  # noqa: BLE001 - fall back to the local artifact
            logger.warning("registry_load_failed", error=str(exc))

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
        """Predict a support band and per-class probabilities for each row."""
        if self.pipeline is None:
            raise RuntimeError("model not loaded")

        frame = pd.DataFrame(rows)
        order = self.feature_order
        if order:
            frame = frame[order]

        if hasattr(self.pipeline, "predict_proba"):
            probabilities = self.pipeline.predict_proba(frame)
            classes = list(self.pipeline.named_steps["clf"].classes_)
            predictions = apply_thresholds(
                probabilities, classes, self.decision_thresholds
            )
        else:  # pragma: no cover - all catalog models expose predict_proba
            predictions = [str(value) for value in self.pipeline.predict(frame)]
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
                    "support_band": support_band(str(label), self.support_bands),
                    "probabilities": row,
                    "confidence": float(max(row.values())),
                }
            )
        return results


_store = ModelStore()


def get_store() -> ModelStore:
    """Return the process-wide model store."""
    return _store
