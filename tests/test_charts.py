"""Feature and end-to-end tests for saved Chart Studio views."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from analytics.db import delete_view, get_engine, init_db, list_views, save_view
from api.main import app

client = TestClient(app)
SPEC = {"type": "bar", "x": "Class", "y": "raisedhands", "aggregate": "mean"}


# --------------------------------------------------------------------- feature
def test_save_list_delete_view_roundtrip(tmp_path: Path):
    engine = get_engine(f"sqlite:///{tmp_path / 'views.db'}")
    init_db(engine)

    saved = save_view(engine, "Behaviour by tier", SPEC)
    assert saved["name"] == "Behaviour by tier"
    assert saved["spec"] == SPEC

    # upsert
    save_view(engine, "Behaviour by tier", {**SPEC, "aggregate": "median"})
    views = list_views(engine)
    assert len(views) == 1
    assert views[0]["spec"]["aggregate"] == "median"

    assert delete_view(engine, "Behaviour by tier") is True
    assert list_views(engine) == []
    assert delete_view(engine, "missing") is False


# ------------------------------------------------------------------------- e2e
def test_charts_endpoints(tmp_path: Path, monkeypatch):
    db_url = f"sqlite:///{tmp_path / 'api.db'}"
    init_db(get_engine(db_url))
    monkeypatch.setenv("DATABASE_URL", db_url)

    created = client.post("/charts", json={"name": "My view", "spec": SPEC})
    assert created.status_code == 200
    assert created.json()["name"] == "My view"

    listed = client.get("/charts")
    assert listed.status_code == 200
    assert any(view["name"] == "My view" for view in listed.json())

    deleted = client.delete("/charts/My view")
    assert deleted.status_code == 200
    assert client.delete("/charts/My view").status_code == 404
