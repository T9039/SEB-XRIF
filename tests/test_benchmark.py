"""Feature and end-to-end tests for the comparison-matrix benchmark."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

from analytics.benchmark import (
    METRIC_COLUMNS,
    run_benchmark,
    to_markdown,
    write_reports,
)
from analytics.config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[1]
FAST_MODELS = ["dummy", "decision_tree"]


# --------------------------------------------------------------------- feature
def test_run_benchmark_returns_ranked_table():
    results = run_benchmark(models=FAST_MODELS, folds=3, verbose=False)

    assert list(results["model"]) == FAST_MODELS or set(results["model"]) == set(
        FAST_MODELS
    )
    for column in METRIC_COLUMNS:
        assert column in results.columns
    ok = results[results["status"] == "ok"]
    assert not ok.empty
    assert ok["cv_mean"].between(0.0, 1.0).all()
    assert (ok["cv_ci_low"] <= ok["cv_mean"]).all()
    assert (ok["cv_mean"] <= ok["cv_ci_high"]).all()
    # Sorted by CV macro F1 descending.
    assert ok["cv_mean"].is_monotonic_decreasing or len(ok) == 1


def test_write_reports_creates_csv_markdown_json(tmp_path: Path):
    results = run_benchmark(models=FAST_MODELS, folds=3, verbose=False)
    written = write_reports(results, tmp_path, folds=3, make_figure=False)

    assert written["csv"].exists()
    assert written["markdown"].exists()
    assert written["json"].exists()

    md = written["markdown"].read_text(encoding="utf-8")
    for model in FAST_MODELS:
        assert model in md
    assert "benchmark" in md.lower()

    reloaded = pd.read_csv(written["csv"])
    assert set(reloaded["model"]) == set(FAST_MODELS)


def test_write_reports_can_render_figure(tmp_path: Path):
    results = run_benchmark(models=["decision_tree"], folds=3, verbose=False)
    written = write_reports(results, tmp_path, folds=3, make_figure=True)
    assert written["figure"].exists()
    assert written["figure"].stat().st_size > 0


def test_to_markdown_handles_failed_models():
    results = pd.DataFrame(
        [
            {
                "model": "broken",
                "status": "error: boom",
                "accuracy": None,
                "f1_macro": None,
                "cv_mean": None,
                "cv_std": None,
                "roc_auc_ovr": None,
                "fit_seconds": None,
            }
        ]
    )
    md = to_markdown(results, folds=5)
    assert "broken" in md
    assert "error: boom" in md


# ------------------------------------------------------------------------- e2e
def test_benchmark_cli_end_to_end(tmp_path: Path):
    """Invoke the module exactly as a user would and check the artifacts."""
    env = {"PYTHONPATH": str(REPO_ROOT)}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "analytics.benchmark",
            "--models",
            "dummy",
            "logistic_regression",
            "--cv",
            "3",
            "--out",
            str(tmp_path),
            "--no-figure",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "results.csv").exists()
    assert (tmp_path / "results.md").exists()
    assert "Best by CV macro F1" in completed.stdout


def test_settings_exposes_reports_dir():
    settings = get_settings()
    assert settings.reports_dir.name == "reports"
