"""Per-source training: artifact paths, single model, and best-of-matrix."""

from __future__ import annotations

import json
from dataclasses import replace

from analytics.config import get_settings
from analytics.data import load_raw
from analytics.datasets.uploads import write_upload
from analytics.train import train_source
from analytics.xapi import build_statements, learner_id

UPLOAD = "my-pilot"


def _statements_text(n: int) -> str:
    statements: list[dict] = []
    for index, (_, row) in enumerate(load_raw().head(n).iterrows()):
        statements.extend(build_statements(row.to_dict(), learner_id(index)))
    return "\n".join(json.dumps(statement) for statement in statements)


def _settings(tmp_path):
    settings = replace(get_settings(), repo_root=tmp_path, cv_folds=3, n_jobs=1)
    write_upload(
        UPLOAD,
        _statements_text(60),
        description="test upload",
        target="Class",
        class_labels=["L", "M", "H"],
        settings=settings,
    )
    return replace(settings, dataset=UPLOAD)


def test_train_source_writes_per_source_artifacts(tmp_path):
    settings = _settings(tmp_path)
    train_source(UPLOAD, settings, models=["decision_tree"], no_mlflow=True)

    model_path, metadata_path, run_path = settings.artifacts_for(UPLOAD)
    assert model_path.name == f"{UPLOAD}.joblib"
    assert model_path.exists()
    assert metadata_path.exists()
    assert run_path.exists()
    assert settings.shap_for(UPLOAD).exists()

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["source"] == UPLOAD
    assert metadata["target"] == "Class"
    assert metadata["model"] == "decision_tree"
    assert metadata["feature_order"]


def test_matrix_promotes_the_best_model(tmp_path, monkeypatch):
    settings = _settings(tmp_path)
    monkeypatch.setattr(
        "analytics.train.model_catalog", lambda: ["dummy", "decision_tree"]
    )
    promoted = train_source(UPLOAD, settings, matrix=True, no_mlflow=True)
    assert promoted["model"] in {"dummy", "decision_tree"}
    assert promoted["source"] == UPLOAD


def test_kalboard_keeps_its_legacy_paths(tmp_path):
    settings = replace(get_settings(), repo_root=tmp_path)
    model_path, metadata_path, run_path = settings.artifacts_for("kalboard")
    assert model_path == settings.model_path
    assert metadata_path == settings.metadata_path
    assert run_path == settings.run_path
