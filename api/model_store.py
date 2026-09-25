"""Artifact loading and inference for the API.

Loads a promoted pipeline and its sidecars per source, either from the local
joblib artifact or (for Kalboard) the MLflow model registry. Stores are cached
per source and loaded lazily. If no model exists the service still starts and
reports a degraded state; prediction routes return HTTP 503 until a model is
available.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from analytics.config import get_settings as get_analytics_settings
from analytics.decision import apply_thresholds, support_band

from .config import ApiSettings, get_api_settings
from .logging import get_logger

logger = get_logger("api.model_store")


class ModelStore:
    """Holds one source's loaded pipeline, metadata, and explanation payloads."""

    def __init__(self, source: str = "kalboard") -> None:
        self.source = source
        self.pipeline: Any | None = None
        self.metadata: dict[str, Any] = {}
        self.shap: dict[str, Any] = {}
        self.support_bands: dict[str, str] = {}
        self.decision_thresholds: dict[str, float] = {}

    def _paths(self) -> tuple[Path, Path, Path, Path]:
        """Return the model, metadata, run, and SHAP paths for this source."""
        if self.source == "kalboard":
            api = get_api_settings()
            return (
                api.model_path,
                api.metadata_path,
                api.run_path,
                api.shap_path,
            )
        analytics = get_analytics_settings()
        model_path, metadata_path, run_path = analytics.artifacts_for(self.source)
        return model_path, metadata_path, run_path, analytics.shap_for(self.source)

    def load(self, source: str | None = None) -> ModelStore:
        """Load the pipeline and sidecars for the configured source."""
        if source:
            self.source = source
        analytics = get_analytics_settings()
        self.support_bands = dict(analytics.support_bands)
        self.decision_thresholds = dict(analytics.decision_thresholds)

        api = get_api_settings()
        model_path, metadata_path, run_path, shap_path = self._paths()

        if api.model_source == "registry" and self.source == "kalboard":
            self._load_from_registry(api)
        if self.pipeline is None and model_path.exists():
            self.pipeline = joblib.load(model_path)
            logger.info("model_loaded", source=self.source, path=str(model_path))

        if metadata_path.exists():
            self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if run_path.exists():
            run = json.loads(run_path.read_text(encoding="utf-8"))
            self.metadata = {**self.metadata, **run}
        if shap_path.exists():
            self.shap = json.loads(shap_path.read_text(encoding="utf-8"))
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
            missing = [column for column in order if column not in frame.columns]
            if missing:
                raise ValueError(
                    f"missing required features for source '{self.source}': {missing}"
                )
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


_STORES: dict[str, ModelStore] = {}


def get_store(source: str = "kalboard") -> ModelStore:
    """Return the process-wide store for a source, loading it on first use."""
    store = _STORES.get(source)
    if store is None:
        store = ModelStore(source).load()
        _STORES[source] = store
    return store


def clear_stores() -> None:
    """Drop every cached store (used by tests)."""
    _STORES.clear()
