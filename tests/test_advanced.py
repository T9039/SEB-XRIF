"""Feature and end-to-end tests for the advanced analytics."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import joblib
import pytest
from fastapi.testclient import TestClient

from analytics.config import get_settings
from analytics.embedding import compute_embedding
from analytics.pdp import compute_pdp
from analytics.train import train_model
from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _empty_database(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empty.db'}")


# --------------------------------------------------------------------- feature
def test_embedding_shape():
    payload = compute_embedding(get_settings(), n_clusters=3)
    assert len(payload["points"]) == 480
    assert set(payload["clusters"]) == {"0", "1", "2"}
    assert len(payload["profiles"]) == 4  # four behavioural features
    assert len(payload["explained_variance"]) == 2
    point = payload["points"][0]
    assert {"x", "y", "tier", "cluster"} <= set(point)


def test_pdp_curve(tmp_path: Path):
    settings = get_settings()
    result = train_model("decision_tree", settings)
    model_path = tmp_path / "model.joblib"
    joblib.dump(result["pipeline"], model_path)
    local = dataclasses.replace(
        settings, paths={**settings.paths, "model": str(model_path)}, n_jobs=1
    )

    payload = compute_pdp("raisedhands", local, grid_points=10)
    assert payload["feature"] == "raisedhands"
    assert len(payload["rows"]) == 10
    assert set(payload["classes"]) == {"L", "M", "H"}

    with pytest.raises(KeyError):
        compute_pdp("not_a_feature", local)


# ------------------------------------------------------------------------- e2e
def test_advanced_endpoints():
    embedding = client.get("/analytics/embedding")
    assert embedding.status_code == 200
    assert len(embedding.json()["points"]) == 480

    pdp = client.get("/model/pdp", params={"feature": "raisedhands"})
    assert pdp.status_code in {200, 503}
    if pdp.status_code == 200:
        assert pdp.json()["rows"]
