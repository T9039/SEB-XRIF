"""Feature and end-to-end tests for model serving parity and hardening."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from analytics.config import get_settings
from analytics.train import train_model
from api.config import get_api_settings
from api.main import app
from api.model_store import ModelStore, clear_stores, get_store

SAMPLE = {
    "gender": "M",
    "NationalITy": "KW",
    "PlaceofBirth": "KuwaIT",
    "StageID": "lowerlevel",
    "GradeID": "G-04",
    "SectionID": "A",
    "Topic": "IT",
    "Semester": "F",
    "Relation": "Father",
    "ParentAnsweringSurvey": "Yes",
    "ParentschoolSatisfaction": "Good",
    "StudentAbsenceDays": "Under-7",
    "raisedhands": 15,
    "VisITedResources": 16,
    "AnnouncementsView": 2,
    "Discussion": 20,
}


@pytest.fixture
def served_model(tmp_path: Path, monkeypatch):
    """Train a small model, persist it to temp paths, and reload the store."""
    monkeypatch.setenv("SEBXRIF_MODEL_PATH", str(tmp_path / "model.joblib"))
    monkeypatch.setenv("SEBXRIF_METADATA_PATH", str(tmp_path / "model.meta.json"))
    monkeypatch.setenv("SEBXRIF_RUN_PATH", str(tmp_path / "model.run.json"))
    monkeypatch.setenv("SEBXRIF_SHAP_PATH", str(tmp_path / "shap.json"))
    get_api_settings.cache_clear()

    settings = get_settings()
    result = train_model("decision_tree", settings)
    joblib.dump(result["pipeline"], tmp_path / "model.joblib")
    (tmp_path / "model.meta.json").write_text(
        json.dumps(
            {"feature_order": result["features"], "model_version": "test-decision-tree"}
        ),
        encoding="utf-8",
    )

    clear_stores()
    store = get_store()
    store.load()
    yield result

    get_api_settings.cache_clear()
    clear_stores()


# --------------------------------------------------------------------- feature
def test_store_predict_matches_pipeline(served_model):
    result = served_model
    pipeline = result["pipeline"]
    features = result["features"]

    rows = [
        dict(SAMPLE),
        dict(SAMPLE, raisedhands=60, VisITedResources=70, Discussion=90),
    ]
    served = ModelStore().load().predict(rows)

    frame = pd.DataFrame(rows)[features]
    direct = pipeline.predict(frame)
    proba = pipeline.predict_proba(frame)
    classes = list(pipeline.named_steps["clf"].classes_)

    assert [item["prediction"] for item in served] == [str(value) for value in direct]
    for index, item in enumerate(served):
        assert item["confidence"] == pytest.approx(float(max(proba[index])), abs=1e-9)
        for column, label in enumerate(classes):
            assert item["probabilities"][str(label)] == pytest.approx(
                float(proba[index][column]), abs=1e-9
            )


# ------------------------------------------------------------------------- e2e
def test_predict_endpoint_with_loaded_model(served_model):
    client = TestClient(app)
    response = client.post("/predict", json=SAMPLE)
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in {"L", "M", "H"}
    assert body["support_band"] in {"priority-support", "monitor", "on-track"}
    assert 0.0 <= body["confidence"] <= 1.0


def test_version_endpoint(served_model):
    client = TestClient(app)
    body = client.get("/version").json()
    assert body["model_loaded"] is True
    assert body["model_version"] == "test-decision-tree"
    assert "python" in body


def test_request_id_is_echoed(served_model):
    client = TestClient(app)
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"
