"""Feature and end-to-end tests for the Postgres/CSV data source."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from analytics.data import load_source, read_learners
from analytics.db import counts, get_engine, init_db, session_scope, upsert_learner
from analytics.xapi import to_learner_dict
from api.main import app

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


def _seed(url: str, n: int = 3) -> None:
    engine = get_engine(url)
    init_db(engine)
    with session_scope(engine) as session:
        for index in range(n):
            row = dict(LEARNER, raisedhands=10 + index)
            upsert_learner(session, to_learner_dict(row, f"L{index:04d}"))


# --------------------------------------------------------------------- feature
def test_load_source_defaults_to_csv(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empty.db'}")
    frame, source = load_source()
    assert source == "csv"
    assert len(frame) == 480


def test_read_learners_falls_back_to_csv(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empty.db'}")
    frame, source = read_learners(prefer_db=True)
    assert source == "csv"
    assert len(frame) == 480


# ------------------------------------------------------------------------- e2e
def test_read_learners_uses_postgres_when_populated(monkeypatch, tmp_path: Path):
    url = f"sqlite:///{tmp_path / 'seeded.db'}"
    _seed(url, 3)
    monkeypatch.setenv("DATABASE_URL", url)

    frame, source = read_learners(prefer_db=True)
    assert source == "postgres"
    assert len(frame) == 3


def test_api_trends_reports_postgres_source(monkeypatch, tmp_path: Path):
    url = f"sqlite:///{tmp_path / 'seeded.db'}"
    _seed(url, 5)
    monkeypatch.setenv("DATABASE_URL", url)

    client = TestClient(app)
    response = client.get("/trends")
    assert response.status_code == 200
    body = response.json()
    assert body["data_source"] == "postgres"
    assert body["total_records"] == 5
    assert counts(get_engine(url))["learners"] == 5
