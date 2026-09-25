"""ARETE XR adapter: parsing every pilot, feature derivation, schema, trends."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from analytics import xr
from analytics.xr_schema import VERB_FEATURES, verb_class
from api.main import app

FIXDIR = Path(__file__).parent / "fixtures" / "arete"
FIXTURES: dict[str, Path] = {
    "pbis": FIXDIR / "xAPI_PBIS.sample.csv",
    "english-literacy": FIXDIR / "EnglishLiteracy-Anonymized.sample.csv",
    "stem-geometry": FIXDIR / "STEMGeometry.sample.csv",
    "stem-geography": FIXDIR / "STEMGeography.sample.csv",
    "lxd": FIXDIR / "LXD.sample.csv",
}
CASES = list(FIXTURES.items())


# ------------------------------------------------------------------- parsing
@pytest.mark.parametrize(("pilot", "fixture"), CASES)
def test_parse_statements_is_tidy(pilot, fixture):
    statements = xr.parse_statements(fixture)
    assert len(statements) > 50
    assert {
        "timestamp",
        "learner",
        "verb",
        "object",
        "result_raw",
        "result_response",
        "language",
    } <= set(statements.columns)
    assert statements["timestamp"].notna().all()
    verbs = statements["verb"].dropna()
    assert verbs.str.lower().eq(verbs).all()


def test_delimiters_and_displays_are_normalised():
    pbis = xr.parse_statements(FIXTURES["pbis"])
    english = xr.parse_statements(FIXTURES["english-literacy"])
    # PBIS is ';'-delimited with plain displays; English is ','-delimited with
    # dict-string displays. Both yield a clean lowercase verb.
    assert "selected" in set(pbis["verb"])
    assert "selected" in set(english["verb"])


def test_result_shapes_are_parsed():
    english = xr.parse_statements(FIXTURES["english-literacy"])
    assert english["result_raw"].notna().all()
    geometry = xr.parse_statements(FIXTURES["stem-geometry"])
    assert geometry["result_raw"].notna().any()
    lxd = xr.parse_statements(FIXTURES["lxd"])
    assert lxd["result_raw"].notna().any()


def test_optional_columns_differ_by_pilot():
    # Only PBIS carries textual responses; only STEM carries a language column.
    assert xr.parse_statements(FIXTURES["pbis"])["result_response"].notna().any()
    assert xr.parse_statements(FIXTURES["stem-geometry"])["language"].notna().any()
    assert xr.parse_statements(FIXTURES["lxd"])["language"].isna().all()


def test_verb_class_mapping():
    assert verb_class("Selected") == "interaction"
    assert verb_class("measured") == "content"
    assert verb_class("left") == "disengagement"
    assert verb_class("a-verb-nobody-defined") == "other"


# -------------------------------------------------------------- feature frame
@pytest.mark.parametrize(("pilot", "fixture"), CASES)
def test_derive_features_validates_against_schema(pilot, fixture):
    statements = xr.parse_statements(fixture)
    features = xr.derive_learner_features(statements)
    validated = xr.validate_features(features)
    assert len(validated) == statements["learner"].nunique()
    assert int(validated["events"].sum()) == len(statements)
    assert (validated["active_days"] >= 1).all()
    assert set(validated.columns) >= set(VERB_FEATURES)


@pytest.mark.parametrize(("pilot", "fixture"), CASES)
def test_engagement_trends_buckets(pilot, fixture):
    statements = xr.parse_statements(fixture)
    trends = xr.engagement_trends(statements, freq="W")
    assert trends["events"] == len(statements)
    assert trends["learners"] == statements["learner"].nunique()
    assert len(trends["period_start"]) == len(trends["events_by_period"])
    assert sum(trends["events_by_period"]) == trends["events"]
    assert sum(trends["active_learners_by_period"]) >= trends["learners"]


def test_unknown_pilot_raises():
    with pytest.raises(ValueError, match="Unknown ARETE pilot"):
        xr.get_pilot("does-not-exist")


def test_all_pilots_registered():
    assert set(xr.PILOTS) == set(FIXTURES)


def test_unsupported_frequency_raises():
    statements = xr.parse_statements(FIXTURES["pbis"])
    with pytest.raises(ValueError, match="Unsupported frequency"):
        xr.engagement_trends(statements, freq="Y")


# -------------------------------------------------------------------- service
def test_xr_pilots_endpoint_lists_all():
    body = TestClient(app).get("/xr/pilots").json()
    assert body["licence"] == "CC BY 4.0"
    assert {pilot["name"] for pilot in body["pilots"]} == set(FIXTURES)


@pytest.mark.parametrize(("pilot", "fixture"), CASES)
def test_xr_trends_endpoint_serves_each_pilot(monkeypatch, pilot, fixture):
    monkeypatch.setattr(xr, "pilot_path", lambda p, settings=None: FIXTURES[p.name])
    response = TestClient(app).get("/xr/trends", params={"pilot": pilot, "freq": "M"})
    assert response.status_code == 200
    body = response.json()
    assert body["pilot"] == pilot
    assert body["events"] == len(xr.parse_statements(fixture))
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
