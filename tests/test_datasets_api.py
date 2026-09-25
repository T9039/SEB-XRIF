"""Upload API: list, upload, validate, delete, and train a source."""

from __future__ import annotations

import json
from dataclasses import replace

from fastapi.testclient import TestClient

from analytics.config import get_settings
from analytics.data import load_raw
from analytics.xapi import build_statements, learner_id
from api.main import app
from api.routes import datasets as datasets_route

NAME = "upload-api"


def _statements_text(n: int = 40, *, target: bool = True) -> str:
    completed = "http://adlnet.gov/expapi/verbs/completed"
    statements: list[dict] = []
    for index, (_, row) in enumerate(load_raw().head(n).iterrows()):
        batch = build_statements(row.to_dict(), learner_id(index))
        if not target:
            batch = [s for s in batch if s["verb"]["id"] != completed]
        statements.extend(batch)
    return "\n".join(json.dumps(statement) for statement in statements)


def _settings(tmp_path, monkeypatch):
    settings = replace(get_settings(), repo_root=tmp_path, cv_folds=3, n_jobs=1)
    monkeypatch.setattr(datasets_route, "get_settings", lambda: settings)
    return settings


def _upload(client: TestClient, name: str = NAME, text: str | None = None):
    return client.post(
        "/datasets",
        data={
            "name": name,
            "description": "demo",
            "target": "Class",
            "class_labels": "L,M,H",
        },
        files={
            "file": ("statements.jsonl", text or _statements_text(), "application/json")
        },
    )


def test_upload_list_delete(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)

    response = _upload(client)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["learners"] == 40
    assert body["target"] == "Class"

    sources = {
        source["name"]: source for source in client.get("/datasets").json()["sources"]
    }
    assert sources[NAME]["kind"] == "upload"
    assert sources[NAME]["trained"] is False

    assert client.delete(f"/datasets/{NAME}").status_code == 200
    assert NAME not in {s["name"] for s in client.get("/datasets").json()["sources"]}


def test_train_endpoint_promotes_a_model(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    _upload(client)

    response = client.post(
        f"/datasets/{NAME}/train", params={"mode": "single", "model": "decision_tree"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["model"] == "decision_tree"

    sources = {
        source["name"]: source for source in client.get("/datasets").json()["sources"]
    }
    assert sources[NAME]["trained"] is True


def test_upload_rejects_non_conformant_file(tmp_path, monkeypatch):
    settings = _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    response = _upload(client, text=_statements_text(target=False))
    assert response.status_code == 400
    # The failed upload must not leave files behind.
    assert not (settings.uploads_dir / f"{NAME}.json").exists()


def test_upload_rejects_bad_name(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    assert _upload(client, name="Bad Name!").status_code == 400


def test_delete_rejects_builtin(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    assert client.delete("/datasets/kalboard").status_code == 400
