"""Early-warning XR engagement/risk model and its endpoint."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from analytics import xr, xr_risk
from api.main import app

BASE = pd.Timestamp("2023-01-01", tz="UTC")


def synthetic_statements() -> pd.DataFrame:
    """30 learners return a week later; 30 drop off after the first session."""
    rows: list[dict] = []
    for index in range(60):
        engaged = index < 30
        learner = f"L{index:03d}"
        early_verbs = (
            ["selected", "completed", "responded"]
            if engaged
            else ["skipped", "selected", "left"]
        )
        start = BASE + pd.Timedelta(seconds=index)
        for j in range(10):
            rows.append(
                {
                    "timestamp": start + pd.Timedelta(minutes=j),
                    "learner": learner,
                    "verb": early_verbs[j % len(early_verbs)],
                    "object": f"obj{j % 3}",
                    "result_raw": 1.0 if (engaged and j % 2 == 0) else np.nan,
                    "result_response": pd.NA,
                    "language": pd.NA,
                }
            )
        for j in range(10 if engaged else 0):
            rows.append(
                {
                    "timestamp": start + pd.Timedelta(days=7, minutes=j),
                    "learner": learner,
                    "verb": "selected",
                    "object": f"obj{j % 2}",
                    "result_raw": 1.0 if j % 2 == 0 else np.nan,
                    "result_response": pd.NA,
                    "language": pd.NA,
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture(autouse=True)
def _clear_cache():
    xr_risk.clear_cache()
    yield
    xr_risk.clear_cache()


# --------------------------------------------------------------------- feature
def test_build_dataset_labels_late_dropoff():
    features, labels = xr_risk.build_dataset(synthetic_statements())
    assert len(features) == 60
    assert set(labels.unique()) == {0, 1}
    assert int(labels.sum()) == 30


def test_analyse_reports_early_warning_metrics():
    payload = xr_risk.analyse(synthetic_statements(), folds=5)
    assert payload["available"] is True
    assert payload["n"] == 60
    assert payload["positives"] == 30
    assert 0.0 <= payload["brier"] <= 1.0
    assert payload["roc_auc"] > 0.7
    assert payload["average_precision"] > 0.7
    assert len(payload["features"]) == len(payload["importances"]) or set(
        payload["importances"]
    ) <= set(payload["features"])
    assert sum(payload["bands"].values()) == payload["n"]
    risks = [learner["risk"] for learner in payload["learners"]]
    assert risks == sorted(risks, reverse=True)


def test_analyse_refuses_a_single_class_cohort():
    statements = synthetic_statements()
    engaged_only = statements[statements["learner"].str[1:].astype(int) < 30]
    payload = xr_risk.analyse(engaged_only)
    assert payload["available"] is False


def test_risk_band_thresholds():
    assert xr_risk.risk_band(0.9) == "elevated"
    assert xr_risk.risk_band(0.5) == "watch"
    assert xr_risk.risk_band(0.1) == "retained"


# -------------------------------------------------------------------- service
def test_xr_risk_endpoint(monkeypatch):
    statements = synthetic_statements()
    monkeypatch.setattr(
        xr,
        "load_pilot",
        lambda name, settings=None, path=None: (statements, xr.PILOTS["pbis"]),
    )
    response = TestClient(app).get("/xr/risk", params={"pilot": "pbis", "folds": 5})
    assert response.status_code == 200
    body = response.json()
    assert body["pilot"] == "pbis"
    assert body["available"] is True
    assert body["roc_auc"] > 0.7


def test_xr_risk_missing_pilot_is_503(monkeypatch, tmp_path):
    monkeypatch.setattr(
        xr, "pilot_path", lambda pilot, settings=None: tmp_path / "missing.csv"
    )
    response = TestClient(app).get("/xr/risk", params={"pilot": "pbis"})
    assert response.status_code == 503


def test_xr_risk_unknown_pilot_is_404():
    response = TestClient(app).get("/xr/risk", params={"pilot": "nope"})
    assert response.status_code == 404
