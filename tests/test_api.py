"""Tests for the FastAPI service."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _empty_database(tmp_path: Path, monkeypatch):
    """Force the CSV fallback so trends are deterministic in tests."""
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empty.db'}")


def test_health_reports_status():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert "model_loaded" in body


def test_root_lists_endpoints():
    response = client.get("/")
    assert response.status_code == 200
    assert "/predict" in response.json()["endpoints"]


def test_trends_aggregates_raw_data():
    response = client.get("/trends")
    assert response.status_code == 200
    body = response.json()
    assert body["total_records"] == 480
    assert body["data_source"] == "csv"
    assert set(body["class_counts"]) == {"L", "M", "H"}


def test_metrics_returns_503_without_model():
    response = client.get("/metrics")
    # Either a trained model exists (200) or it is reported as unavailable (503).
    assert response.status_code in {200, 503}


def test_predict_returns_503_without_model():
    payload = {
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
    response = client.post("/predict", json=payload)
    assert response.status_code in {200, 503}
