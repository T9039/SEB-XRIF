"""Reproducibility: deterministic metadata, separate run provenance."""

from __future__ import annotations

import json
from dataclasses import replace

from analytics.config import get_settings
from analytics.train import save_artifact, train_model
from api.config import get_api_settings
from api.model_store import ModelStore


def test_metadata_is_deterministic_and_provenance_is_separate(tmp_path):
    real = get_settings()
    result = train_model("decision_tree", real)
    settings = replace(real, repo_root=tmp_path)

    merged = save_artifact(result, settings)
    metadata = json.loads(settings.metadata_path.read_text(encoding="utf-8"))
    run = json.loads(settings.run_path.read_text(encoding="utf-8"))

    for volatile in ("created_utc", "git_commit", "model_version"):
        assert volatile not in metadata
    assert set(run) == {"model_version", "created_utc", "git_commit"}
    assert merged["model_version"] == run["model_version"]

    first = settings.metadata_path.read_text(encoding="utf-8")
    save_artifact(result, settings)
    assert settings.metadata_path.read_text(encoding="utf-8") == first


def test_api_metadata_merges_run_provenance(tmp_path, monkeypatch):
    monkeypatch.setenv("SEBXRIF_METADATA_PATH", str(tmp_path / "model.meta.json"))
    monkeypatch.setenv("SEBXRIF_RUN_PATH", str(tmp_path / "model.run.json"))
    get_api_settings.cache_clear()

    (tmp_path / "model.meta.json").write_text(
        json.dumps({"model": "random_forest"}), encoding="utf-8"
    )
    (tmp_path / "model.run.json").write_text(
        json.dumps(
            {
                "model_version": "random_forest-abc123",
                "created_utc": "2026-01-01T00:00:00+00:00",
                "git_commit": "abc123",
            }
        ),
        encoding="utf-8",
    )

    store = ModelStore().load()
    assert store.metadata["model"] == "random_forest"
    assert store.version == "random_forest-abc123"
    assert store.metadata["git_commit"] == "abc123"

    get_api_settings.cache_clear()
