"""Feature and end-to-end tests for xAPI ingestion."""

from __future__ import annotations

from pathlib import Path

import pytest

from analytics.db import counts, get_engine, init_db
from analytics.schema import SCHEMA
from analytics.xapi import (
    BEHAVIOURAL,
    LrsClient,
    build_statements,
    extract_rows,
    frame_from_statements,
    ingest_csv,
    load_rows_into_db,
    to_learner_dict,
)

ROW = {
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


# --------------------------------------------------------------------- feature
def test_build_statements_shape():
    statements = build_statements(ROW, "L0000")
    # one registration + one per behaviour + one completion
    assert len(statements) == 1 + len(BEHAVIOURAL) + 1
    assert all(
        "id" in s and "actor" in s and "verb" in s and "object" in s for s in statements
    )


def test_statement_roundtrip_recovers_the_row():
    statements = build_statements(ROW, "L0000")
    rows = extract_rows(statements)

    assert len(rows) == 1
    recovered = rows[0]
    assert recovered["external_id"] == "L0000"
    assert recovered["gender"] == "M"
    assert recovered["Topic"] == "IT"
    assert recovered["Class"] == "M"
    for behaviour in BEHAVIOURAL:
        assert recovered[behaviour] == ROW[behaviour]


def test_frame_validates_against_schema():
    statements = build_statements(ROW, "L0000")
    frame = frame_from_statements(statements)
    validated = SCHEMA.validate(frame, lazy=True)
    assert len(validated) == 1


def test_to_learner_dict_maps_columns():
    data = to_learner_dict(ROW, "L0000")
    assert data["external_id"] == "L0000"
    assert data["nationality"] == "KW"
    assert data["visited_resources"] == 16
    assert data["target_class"] == "M"


# ------------------------------------------------------------------------- e2e
def test_ingest_read_and_load_roundtrip(tmp_path: Path):
    client = LrsClient()
    if not client.ping():
        pytest.skip("LRS not running")

    posted = ingest_csv(client, limit=3)
    assert posted == 3 * (1 + len(BEHAVIOURAL) + 1)

    statements = client.get_statements(limit=500)
    wanted = {"L0000", "L0001", "L0002"}
    rows = [row for row in extract_rows(statements) if row["external_id"] in wanted]
    assert len(rows) == 3

    url = f"sqlite:///{tmp_path / 'e2e.db'}"
    init_db(get_engine(url))
    loaded = load_rows_into_db(rows, url=url)
    assert loaded == 3
    assert counts(get_engine(url))["learners"] == 3
