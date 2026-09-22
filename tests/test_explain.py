"""Feature and end-to-end tests for interpretability payloads."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from analytics.config import get_settings
from analytics.data import features_and_target, load_validated
from analytics.explain import cross_fold_importance, feature_importance
from analytics.models import build_pipeline

REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------- feature
def test_feature_importance_ranks_features():
    settings = get_settings()
    frame = load_validated(settings=settings)
    features, target = features_and_target(frame, settings)
    pipeline = build_pipeline("decision_tree", settings.seed, settings.n_jobs)
    pipeline.fit(features, target)

    importance = feature_importance(pipeline)
    assert importance
    assert all(isinstance(v, float) for v in importance.values())
    # Ranked descending.
    values = list(importance.values())
    assert values == sorted(values, reverse=True)


def test_cross_fold_importance_reports_stability():
    settings = get_settings()
    frame = load_validated(settings=settings)
    features, target = features_and_target(frame, settings)

    payload = cross_fold_importance(
        lambda: build_pipeline("decision_tree", settings.seed, settings.n_jobs),
        features,
        target,
        folds=3,
        n_repeats=3,
    )

    assert payload["folds"] == 3
    assert len(payload["features"]) == len(features.columns)
    for entry in payload["features"]:
        assert {"feature", "mean", "std"} <= set(entry)


# ------------------------------------------------------------------------- e2e
def test_explain_cli_end_to_end(tmp_path: Path):
    env = {"PYTHONPATH": str(REPO_ROOT)}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "analytics.explain",
            "--model",
            "decision_tree",
            "--folds",
            "3",
            "--out",
            str(tmp_path / "explain.json"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads((tmp_path / "explain.json").read_text(encoding="utf-8"))
    assert payload["model"] == "decision_tree"
    assert "native" in payload
    assert "cross_fold" in payload
