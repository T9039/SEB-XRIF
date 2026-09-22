"""Tests for the comparison-matrix catalog and training smoke path."""

from __future__ import annotations

from analytics.models import SCALE_SENSITIVE, build_pipeline, model_catalog
from analytics.train import train_model


def test_catalog_contains_expected_models():
    catalog = set(model_catalog())
    for name in ["random_forest", "svc", "knn", "logistic_regression", "dummy"]:
        assert name in catalog


def test_scale_sensitive_models_are_registered():
    assert set(model_catalog()) >= SCALE_SENSITIVE


def test_pipelines_build():
    for name in ["random_forest", "svc", "knn"]:
        pipeline = build_pipeline(name, seed=42)
        assert "pre" in pipeline.named_steps
        assert "clf" in pipeline.named_steps


def test_random_forest_trains_and_scores():
    result = train_model("random_forest", settings=None, with_tuning=False)
    metrics = result["metrics"]
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1_macro"] <= 1.0
    assert metrics["confusion_matrix"]
