"""ARETE XR adapter: parsing, feature derivation, schema, and trends."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from analytics import xr
from analytics.xr_schema import VERBS
from api.main import app

FIXTURE = Path(__file__).parent / "fixtures" / "arete" / "xAPI_PBIS.sample.csv"


@pytest.fixture
def statements():
    return xr.parse_statements(FIXTURE)


def test_parse_statements_is_tidy(statements):
    assert {"timestamp", "learner", "verb", "object"} <= set(statements.columns)
    assert len(statements) > 100
    assert statements["timestamp"].notna().all()
    assert statements["verb"].str.lower().eq(statements["verb"]).all()


def test_derive_features_validates_against_schema(statements):
    features = xr.derive_learner_features(statements)
    validated = xr.validate_features(features)
    assert len(validated) == statements["learner"].nunique()
    assert int(validated["events"].sum()) == len(statements)
    assert (validated["active_days"] >= 1).all()
    assert set(validated.columns) >= {f"verb_{verb}" for verb in VERBS}


def test_engagement_trends_buckets(statements):
    trends = xr.engagement_trends(statements, freq="W")
    assert trends["events"] == len(statements)
    assert trends["learners"] == statements["learner"].nunique()
    assert len(trends["period_start"]) == len(trends["events_by_period"])
    assert sum(trends["events_by_period"]) == trends["events"]
    assert sum(trends["active_learners_by_period"]) >= trends["learners"]
    assert set(trends["verb_counts"]) <= set(VERBS)


def test_unknown_pilot_raises():
    with pytest.raises(ValueError, match="Unknown ARETE pilot"):
        xr.get_pilot("does-not-exist")


def test_unsupported_frequency_raises(statements):
    with pytest.raises(ValueError, match="Unsupported frequency"):
        xr.engagement_trends(statements, freq="Y")


def test_xr_pilots_endpoint_lists_pbis():
    body = TestClient(app).get("/xr/pilots").json()
    assert body["licence"] == "CC BY 4.0"
    assert any(pilot["name"] == "pbis" for pilot in body["pilots"])


def test_xr_trends_endpoint_serves_pilot(monkeypatch):
    monkeypatch.setattr(xr, "pilot_path", lambda pilot, settings=None: FIXTURE)
    response = TestClient(app).get("/xr/trends", params={"pilot": "pbis", "freq": "W"})
    assert response.status_code == 200
    body = response.json()
    assert body["pilot"] == "pbis"
    assert body["events"] == len(xr.parse_statements(FIXTURE))
    assert len(body["period_start"]) == len(body["active_learners_by_period"])


def test_xr_trends_missing_pilot_is_503(monkeypatch, tmp_path):
    monkeypatch.setattr(
        xr, "pilot_path", lambda pilot, settings=None: tmp_path / "missing.csv"
    )
    response = TestClient(app).get("/xr/trends", params={"pilot": "pbis"})
    assert response.status_code == 503


def test_xr_trends_unknown_pilot_is_404():
    response = TestClient(app).get("/xr/trends", params={"pilot": "nope"})
    assert response.status_code == 404
