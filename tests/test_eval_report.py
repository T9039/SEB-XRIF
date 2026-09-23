"""Feature and end-to-end tests for the evaluation report."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from analytics.db import evaluations_frame, get_engine, init_db
from eval.report import build_report, to_markdown

REPO_ROOT = Path(__file__).resolve().parents[1]

SUS_PERFECT = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
SUS_LOW = [2, 4, 2, 4, 2, 4, 2, 4, 2, 4]
SUS_RESPONSES = [SUS_PERFECT, SUS_LOW]
T0 = [40, 45, 50, 42, 38]
T1 = [70, 72, 68, 74, 66]
T2 = [60, 64, 58, 62, 56]

PAYLOAD = {"sus": SUS_RESPONSES, "t0": T0, "t1": T1, "t2": T2}


def _report():
    return build_report(sus_responses=SUS_RESPONSES, t0=T0, t1=T1, t2=T2)


# --------------------------------------------------------------------- feature
def test_build_report_computes_usability_and_learning():
    report = _report()

    assert report["usability"]["n"] == 2
    assert report["usability"]["mean"] == 62.5  # (100 + 25) / 2
    assert report["usability"]["meets_benchmark"] is False

    learning = report["learning"]
    assert learning["n"] == 5
    assert learning["gain_immediate"] == 27.0
    assert learning["d_immediate"] > 2.0
    assert learning["retention_ratio"] == pytest.approx(17 / 27)


def test_build_report_supports_immediate_only():
    report = build_report(t0=[1, 2, 3], t1=[3, 4, 5])
    assert "usability" not in report
    assert "d_delayed" not in report["learning"]
    assert report["learning"]["d_immediate"] > 0


def test_markdown_has_the_expected_sections():
    markdown = to_markdown(_report())
    assert markdown.startswith("# Evaluation report")
    assert "## Usability (SUS)" in markdown
    assert "## Learning and retention" in markdown
    assert "Retention ratio" in markdown


# ------------------------------------------------------------------------- e2e
def test_report_cli_writes_files(tmp_path: Path):
    input_path = tmp_path / "pilot.json"
    input_path.write_text(json.dumps(PAYLOAD), encoding="utf-8")
    out = tmp_path / "evaluation.md"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "eval.report",
            "--input",
            str(input_path),
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT)},
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert out.exists()
    assert out.with_suffix(".json").exists()
    assert "Learning and retention" in out.read_text(encoding="utf-8")


def test_report_cli_stores_evaluations(tmp_path: Path, monkeypatch):
    db_url = f"sqlite:///{tmp_path / 'eval.db'}"
    init_db(get_engine(db_url))
    monkeypatch.setenv("DATABASE_URL", db_url)

    input_path = tmp_path / "pilot.json"
    input_path.write_text(json.dumps(PAYLOAD), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "eval.report",
            "--input",
            str(input_path),
            "--out",
            str(tmp_path / "evaluation.md"),
            "--store",
            "--url",
            db_url,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT), "DATABASE_URL": db_url},
        check=False,
    )
    assert completed.returncode == 0, completed.stderr

    frame = evaluations_frame(get_engine(db_url))
    expected = len(T0) + len(T1) + len(T2) + len(SUS_RESPONSES)
    assert len(frame) == expected
    assert set(frame["time_point"]) == {"T0", "T1", "T2"}
    assert "sus" in set(frame["measure"])
