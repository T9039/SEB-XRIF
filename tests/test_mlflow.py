"""Feature and integration tests for MLflow tracking."""

from __future__ import annotations

from pathlib import Path

from analytics.config import get_settings
from analytics.train import _log_mlflow, train_model


# --------------------------------------------------------------------- feature
def test_tracking_uri_prefers_environment(monkeypatch):
    settings = get_settings()
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/seb-xrif-custom")
    assert settings.tracking_uri() == "file:/tmp/seb-xrif-custom"


def test_tracking_uri_defaults_to_config(monkeypatch):
    settings = get_settings()
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    assert settings.tracking_uri() == settings.mlflow_tracking_uri


# ----------------------------------------------------------------- integration
def test_log_mlflow_creates_a_run(tmp_path: Path):
    mlflow = __import__("mlflow")

    settings = get_settings()
    result = train_model("decision_tree", settings)
    metadata = {"git_commit": "test", "model_version": "decision_tree-test"}

    tracking_uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    run_id = _log_mlflow(
        result,
        metadata,
        settings,
        register=False,
        tracking_uri=tracking_uri,
        experiment="seb-xrif-test",
    )

    assert run_id
    assert (tmp_path / "mlflow.db").exists()

    mlflow.set_tracking_uri(tracking_uri)
    runs = mlflow.search_runs(experiment_names=["seb-xrif-test"])
    assert len(runs) >= 1
