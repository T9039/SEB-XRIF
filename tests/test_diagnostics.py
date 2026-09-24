"""Feature and end-to-end tests for model diagnostics."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import joblib
from fastapi.testclient import TestClient

from analytics.config import get_settings
from analytics.diagnostics import compute_diagnostics
from analytics.train import train_model
from api.main import app

client = TestClient(app)


def _settings_with_model(tmp_path: Path):
    settings = get_settings()
    result = train_model("decision_tree", settings)
    model_path = tmp_path / "model.joblib"
    joblib.dump(result["pipeline"], model_path)
    return dataclasses.replace(
        settings,
        paths={**settings.paths, "model": str(model_path)},
        n_jobs=1,
    )


# --------------------------------------------------------------------- feature
def test_compute_diagnostics_shape(tmp_path: Path):
    settings = _settings_with_model(tmp_path)
    payload = compute_diagnostics(settings, folds=3)

    assert set(payload["classes"]) == {"L", "M", "H"}
    assert 0.0 <= payload["macro_auc"] <= 1.0
    assert set(payload["auc"]) == set(payload["classes"])

    assert len(payload["roc"]) == 21
    assert len(payload["pr"]) == 21
    assert len(payload["calibration"]) == 21
    assert len(payload["learning"]) == 5

    for row in payload["roc"]:
        for label in payload["classes"]:
            assert 0.0 <= row[label] <= 1.0
    for row in payload["learning"]:
        assert {"x", "train", "test"} <= set(row)


# ------------------------------------------------------------------------- e2e
def test_diagnostics_endpoint():
    response = client.get("/model/diagnostics")
    # 200 when a model artifact exists, 503 when it has not been trained yet.
    assert response.status_code in {200, 503}
    if response.status_code == 200:
        body = response.json()
        assert "roc" in body and "classes" in body
