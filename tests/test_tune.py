"""Feature and end-to-end tests for Optuna tuning."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from analytics.config import get_settings
from analytics.data import features_and_target, load_validated
from analytics.tune import tunable_models, tune_model

REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------- feature
def test_tunable_models_registered():
    models = set(tunable_models())
    assert {"random_forest", "xgboost", "knn", "svc"}.issubset(models)


def test_tune_model_returns_best_params():
    settings = get_settings()
    frame = load_validated(settings=settings)
    features, target = features_and_target(frame, settings)

    result = tune_model("knn", features, target, n_trials=3, folds=3, seed=1)

    assert result["model"] == "knn"
    assert 0.0 <= result["best_value"] <= 1.0
    assert "n_neighbors" in result["best_params"]


# ------------------------------------------------------------------------- e2e
def test_tune_cli_end_to_end(tmp_path: Path):
    env = {"PYTHONPATH": str(REPO_ROOT)}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "analytics.tune",
            "--models",
            "knn",
            "--trials",
            "3",
            "--cv",
            "3",
            "--out",
            str(tmp_path / "tuning.json"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads((tmp_path / "tuning.json").read_text(encoding="utf-8"))
    assert "knn" in payload
    assert "best_value" in payload["knn"]
