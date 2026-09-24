"""Feature and end-to-end tests for the model-results endpoint."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------- feature
def test_results_endpoint_serves_the_matrix():
    response = client.get("/results")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["results"], list)
    assert len(body["results"]) >= 1
    first = body["results"][0]
    assert {"model", "accuracy", "cv_mean"} <= set(first)


def test_results_endpoint_503_when_missing(monkeypatch, tmp_path: Path):
    from types import SimpleNamespace

    import api.routes.results as route

    monkeypatch.setattr(
        route, "get_settings", lambda: SimpleNamespace(reports_dir=tmp_path)
    )
    response = client.get("/results")
    assert response.status_code == 503


# ------------------------------------------------------------------------- e2e
def test_results_files_exist_for_the_dashboard():
    for name in ("results.json", "tuning.json", "explain.json"):
        assert (REPO_ROOT / "reports" / name).exists(), name
    data = json.loads((REPO_ROOT / "reports" / "results.json").read_text())
    assert len(data) >= 16
