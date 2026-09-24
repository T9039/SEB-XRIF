"""Feature and end-to-end tests for the aggregation/derived-stat engine."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from analytics import aggregate
from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _empty_database(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empty.db'}")


# --------------------------------------------------------------------- feature
def test_column_metadata_describes_columns():
    payload = aggregate.column_metadata()
    kinds = {column["name"]: column["kind"] for column in payload["columns"]}
    assert kinds["Class"] == "categorical"
    assert kinds["Topic"] == "categorical"
    assert kinds["raisedhands"] == "numeric"
    topic = next(c for c in payload["columns"] if c["name"] == "Topic")
    assert "IT" in topic["options"]


def test_run_query_aggregates_by_dimension():
    result = aggregate.run_query(x="Topic", y="raisedhands", aggregate="mean")
    assert result["x"] == "Topic"
    assert result["rows"]
    assert {"x", "value"} <= set(result["rows"][0])
    assert result["total"] == 480


def test_run_query_groups_into_series():
    result = aggregate.run_query(x="Topic", y="raisedhands", group="Class")
    assert set(result["series"]) <= {"L", "M", "H"}
    assert len(result["series"]) >= 1
    for row in result["rows"]:
        assert "x" in row


def test_run_query_filters_and_counts():
    result = aggregate.run_query(x="Class", aggregate="count", filters={"Topic": "IT"})
    assert sum(row["value"] for row in result["rows"]) == result["total"]


def test_correlation_matrix_is_square():
    result = aggregate.correlation()
    n = len(result["columns"])
    assert n >= 4
    assert all(len(row) == n for row in result["matrix"])


def test_distribution_handles_both_kinds():
    categorical = aggregate.distribution("Topic")
    assert categorical["kind"] == "categorical"
    assert sum(row["value"] for row in categorical["rows"]) == 480

    numeric = aggregate.distribution("raisedhands", bins=6)
    assert numeric["kind"] == "numeric"
    assert len(numeric["rows"]) == 6


# ------------------------------------------------------------------------- e2e
def test_analytics_endpoints():
    columns = client.get("/analytics/columns")
    assert columns.status_code == 200

    query = client.post(
        "/analytics/query",
        json={"x": "Class", "y": "VisITedResources", "aggregate": "median"},
    )
    assert query.status_code == 200
    assert query.json()["rows"]

    correlation = client.get("/analytics/correlation")
    assert correlation.status_code == 200
    assert correlation.json()["matrix"]

    distribution = client.get("/analytics/distribution", params={"column": "gender"})
    assert distribution.status_code == 200
    assert distribution.json()["rows"]


def test_analytics_query_rejects_unknown_column():
    response = client.post("/analytics/query", json={"x": "nope"})
    assert response.status_code == 400
