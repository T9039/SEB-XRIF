"""Longitudinal evaluation import, store, summary, and empty state."""

from __future__ import annotations

from fastapi.testclient import TestClient

from analytics.db import get_engine, init_db
from analytics.evaluation import evaluation_summary, import_report
from api.main import app

PAYLOAD = {
    "sus": [
        [4, 2, 5, 1, 4, 2, 5, 1, 4, 1],
        [5, 1, 4, 2, 5, 1, 4, 1, 5, 2],
    ],
    "t0": [40, 42, 38, 44],
    "t1": [70, 68, 74, 72],
    "t2": [62, 60, 66, 64],
}


def test_empty_store_reports_no_data(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empty.db'}")
    summary = evaluation_summary()
    assert summary["available"] is False
    assert "No pilot data" in summary["reason"]


def test_import_then_summary(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'eval.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    init_db(get_engine(url))

    stored = import_report(PAYLOAD, source="pilot", url=url)
    assert stored["scores"] == 12
    assert stored["sus"] == 2

    summary = evaluation_summary(source="pilot")
    assert summary["available"] is True
    assert summary["sources"] == ["pilot"]
    assert summary["usability"]["n"] == 2
    assert summary["usability"]["mean"] > 0
    assert summary["learning"]["n"] == 4
    assert summary["learning"]["d_immediate"] > 0
    assert "mean_t2" in summary["learning"]
    assert "retention_ratio" in summary["learning"]


def test_source_filter_excludes_example_data(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'eval.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    init_db(get_engine(url))
    import_report(PAYLOAD, source="example", url=url)

    assert evaluation_summary(source="pilot")["available"] is False
    assert evaluation_summary(source="example")["available"] is True
    assert evaluation_summary()["available"] is True


def test_evaluation_endpoint_empty_then_populated(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'eval.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    client = TestClient(app)

    empty = client.get("/evaluation").json()
    assert empty["available"] is False

    init_db(get_engine(url))
    import_report(PAYLOAD, source="pilot", url=url)

    populated = client.get("/evaluation", params={"source": "pilot"}).json()
    assert populated["available"] is True
    assert populated["usability"]["n"] == 2
