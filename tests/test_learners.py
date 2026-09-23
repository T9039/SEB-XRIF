"""Feature and end-to-end tests for the learner data endpoints."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from analytics.db import get_engine, init_db, session_scope, upsert_learner
from analytics.xapi import to_learner_dict
from api.main import app

client = TestClient(app)

LEARNER = {
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
    "Class": "M",
}


@pytest.fixture
def empty_database(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empty.db'}")


def _seed(url: str, rows: list[dict]) -> None:
    engine = get_engine(url)
    init_db(engine)
    with session_scope(engine) as session:
        for index, row in enumerate(rows):
            upsert_learner(session, to_learner_dict(row, f"L{index:04d}"))


# --------------------------------------------------------------------- feature
def test_learners_pages_and_reports_source(empty_database):
    response = client.get("/learners", params={"limit": 5})
    assert response.status_code == 200
    body = response.json()
    assert body["data_source"] == "csv"
    assert body["total"] == 480
    assert len(body["rows"]) == 5


def test_learners_filters_by_tier_and_topic(empty_database):
    response = client.get("/learners", params={"class": "H", "limit": 5})
    assert response.status_code == 200
    assert all(row["Class"] == "H" for row in response.json()["rows"])


def test_options_lists_categorical_values(empty_database):
    response = client.get("/options")
    assert response.status_code == 200
    options = response.json()["options"]
    assert "gender" in options
    assert set(options["gender"]) <= {"M", "F"}
    assert "Class" not in options  # target, not a predictor


# ------------------------------------------------------------------------- e2e
def test_learners_uses_postgres_when_seeded(tmp_path: Path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'seeded.db'}"
    _seed(
        url,
        [dict(LEARNER, Topic="IT", **{"Class": "M"})] * 2
        + [dict(LEARNER, Topic="Math", **{"Class": "H"})],
    )
    monkeypatch.setenv("DATABASE_URL", url)

    response = client.get("/learners", params={"topic": "Math"})
    assert response.status_code == 200
    body = response.json()
    assert body["data_source"] == "postgres"
    assert body["total"] == 1
    assert body["rows"][0]["Topic"] == "Math"
