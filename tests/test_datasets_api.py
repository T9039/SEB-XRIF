"""Upload API: check, upload/adapt, list, delete, and train a source."""

from __future__ import annotations

import json
from dataclasses import replace

from fastapi.testclient import TestClient

from analytics.config import get_settings
from analytics.data import load_raw
from analytics.datasets.registry import get_adapter
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


def _csv_text(n: int = 60) -> str:
    lines = ["raisedhands,VisITedResources,AnnouncementsView,Discussion,Class"]
    for index in range(n):
        label = ["L", "M", "H"][index % 3]
        lines.append(
            f"{10 + index % 30},{20 + index % 40},{5 + index % 10},"
            f"{30 + index % 50},{label}"
        )
    return "\n".join(lines)


def _settings(tmp_path, monkeypatch):
    settings = replace(get_settings(), repo_root=tmp_path, cv_folds=3, n_jobs=1)
    monkeypatch.setattr(datasets_route, "get_settings", lambda: settings)
    return settings


def _upload(
    client: TestClient,
    name: str = NAME,
    *,
    filename: str = "statements.jsonl",
    text: str | None = None,
    target: str = "Class",
    train: bool = False,
    mode: str = "single",
    model: str = "decision_tree",
):
    return client.post(
        "/datasets",
        data={
            "name": name,
            "description": "demo",
            "target": target,
            "class_labels": "L,M,H",
            "mode": mode,
            "model": model,
            "train": str(train).lower(),
        },
        files={
            "file": (
                filename,
                text if text is not None else _statements_text(),
                "application/octet-stream",
            )
        },
    )


# --------------------------------------------------------------------- check
def test_check_reports_conformant_statements(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.post(
        "/datasets/check",
        files={"file": ("s.jsonl", _statements_text(10), "application/json")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "statements"
    assert body["conformant"] is True
    assert body["adaptable"] is True


def test_check_suggests_a_table_mapping(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.post(
        "/datasets/check",
        files={"file": ("table.csv", _csv_text(), "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "table"
    assert body["adaptable"] is True
    assert body["suggested_mapping"]["target"] == "Class"
    assert "raisedhands" in body["suggested_mapping"]["features"]


# ------------------------------------------------------------------- upload
def test_upload_and_delete_statements(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)

    response = _upload(client)
    assert response.status_code == 200, response.text
    assert response.json()["kind"] == "statements"
    assert response.json()["learners"] == 40

    sources = {
        source["name"]: source for source in client.get("/datasets").json()["sources"]
    }
    assert sources[NAME]["trained"] is False
    assert client.delete(f"/datasets/{NAME}").status_code == 200


def test_upload_non_conformant_statements_is_422(tmp_path, monkeypatch):
    settings = _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    response = _upload(client, text=_statements_text(target=False))
    assert response.status_code == 422
    assert not (settings.uploads_dir / f"{NAME}.json").exists()


def test_upload_table_adapts_and_trains(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    response = _upload(
        client, filename="table.csv", text=_csv_text(), train=True, mode="single"
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["kind"] == "table"
    assert body["target"] == "Class"
    assert body["trained"] is True
    assert body["model"] == "decision_tree"

    sources = {
        source["name"]: source for source in client.get("/datasets").json()["sources"]
    }
    assert sources[NAME]["trained"] is True


def test_upload_table_without_target_is_422(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    csv = "a,b\n1,2\n3,4\n"
    response = _upload(client, filename="table.csv", text=csv, target="")
    assert response.status_code == 422


def test_upload_rejects_bad_name(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    assert _upload(client, name="Bad Name!").status_code == 400


def test_delete_rejects_builtin(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    assert client.delete("/datasets/kalboard").status_code == 400


# ------------------------------------------------------------------ flatten
def test_flatten_turns_arbitrary_xapi_into_a_table(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    statements = "\n".join(
        json.dumps(
            {
                "actor": {"mbox": f"mailto:l{i}@x"},
                "verb": {"id": "http://foreign/verb/selected"},
                "object": {"id": f"http://foreign/obj/{i}"},
                "timestamp": "2023-01-01T00:00:00Z",
                "result": {"score": {"raw": i}},
            }
        )
        for i in range(3)
    )
    response = client.post(
        "/datasets/flatten",
        files={"file": ("foreign.jsonl", statements, "application/json")},
    )
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/csv")
    text = response.text
    header = text.splitlines()[0]
    assert header.startswith("id,timestamp,actor,verb,object")
    assert len(text.strip().splitlines()) == 4  # header + 3 rows
    assert "http://foreign/verb/selected" in text


def test_flatten_rejects_non_statements(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.post(
        "/datasets/flatten",
        files={"file": ("x.csv", "a,b\n1,2\n", "text/csv")},
    )
    assert response.status_code == 400


# --------------------------------------------------------------- delimiters
def test_check_detects_semicolon_delimiter(tmp_path, monkeypatch):
    _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    csv = "raisedhands;VisITedResources;Class\n5;6;L\n7;8;H\n"
    response = client.post(
        "/datasets/check",
        files={"file": ("semi.csv", csv, "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "table"
    assert body["detected_delimiter"] == ";"
    assert body["adaptable"] is True
    assert body["suggested_mapping"]["target"] == "Class"


def test_semicolon_table_trains_with_stored_delimiter(tmp_path, monkeypatch):
    settings = _settings(tmp_path, monkeypatch)
    client = TestClient(app)
    csv = "raisedhands;VisITedResources;Class\n" + "\n".join(
        f"{i};{i + 1};{['L', 'M', 'H'][i % 3]}" for i in range(40)
    )
    response = client.post(
        "/datasets",
        data={
            "name": "semi-src",
            "target": "Class",
            "mapping": json.dumps({"delimiter": ";"}),
            "mode": "single",
            "model": "decision_tree",
            "train": "false",
        },
        files={"file": ("semi.csv", csv, "text/csv")},
    )
    assert response.status_code == 200, response.text

    # The sidecar remembers the delimiter and the adapter reads it back.
    sidecar = json.loads((settings.uploads_dir / "semi-src.json").read_text())
    assert sidecar["delimiter"] == ";"
    dataset = get_adapter("semi-src", settings).load(settings)
    assert len(dataset.frame) == 40
    assert "raisedhands" in dataset.frame.columns
