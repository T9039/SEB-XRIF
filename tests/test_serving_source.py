"""Per-source serving: predict, metrics, and diagnostics accept a source."""

from __future__ import annotations

import json
from dataclasses import replace

from fastapi.testclient import TestClient

from analytics.config import get_settings
from analytics.data import load_raw
from analytics.datasets.uploads import write_upload
from analytics.train import train_source
from analytics.xapi import build_statements, learner_id
from api import model_store
from api.main import app
from api.routes import diagnostics as diagnostics_route
from api.routes import predict as predict_route

SOURCE = "serve-pilot"

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


def _settings(tmp_path):
    settings = replace(get_settings(), repo_root=tmp_path, cv_folds=3, n_jobs=1)
    statements: list[dict] = []
    for index, (_, row) in enumerate(load_raw().head(60).iterrows()):
        statements.extend(build_statements(row.to_dict(), learner_id(index)))
    write_upload(
        SOURCE,
        "\n".join(json.dumps(statement) for statement in statements),
        target="Class",
        class_labels=["L", "M", "H"],
        settings=settings,
    )
    return replace(settings, dataset=SOURCE)


def _prepare(tmp_path, monkeypatch):
    settings = _settings(tmp_path)
    train_source(SOURCE, settings, models=["decision_tree"], no_mlflow=True)
    monkeypatch.setattr(model_store, "get_analytics_settings", lambda: settings)
    monkeypatch.setattr(diagnostics_route, "get_settings", lambda: settings)
    monkeypatch.setattr(predict_route, "get_settings", lambda: settings)
    model_store.clear_stores()
    return settings


def test_predict_and_metrics_are_source_scoped(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    client = TestClient(app)

    response = client.post(f"/predict?source={SOURCE}", json=SAMPLE)
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in {"L", "M", "H"}
    assert "support_band" in body

    metrics = client.get(f"/metrics?source={SOURCE}").json()
    assert metrics["source"] == SOURCE
    assert metrics["model"] == "decision_tree"


def test_diagnostics_are_source_scoped(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.get(f"/model/diagnostics?source={SOURCE}")
    assert response.status_code == 200
    assert set(response.json()["classes"]) == {"L", "M", "H"}


def test_unknown_source_has_no_metrics(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    client = TestClient(app)
    assert client.get("/metrics?source=does-not-exist").status_code == 503


def test_model_features_describe_the_source(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    client = TestClient(app)
    body = client.get(f"/model/features?source={SOURCE}").json()
    assert body["source"] == SOURCE
    assert body["target"] == "Class"
    assert "raisedhands" in body["features"]
    assert "gender" in body["categorical"]
    assert "raisedhands" in body["numeric"]
    assert body["options"]["gender"]
    assert client.get("/model/features?source=nope").status_code == 404
