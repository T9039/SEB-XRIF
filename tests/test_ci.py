"""Feature and end-to-end tests for the CI workflow and tooling."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def load_ci() -> dict:
    return yaml.safe_load(CI.read_text(encoding="utf-8"))


# --------------------------------------------------------------------- feature
def test_ci_has_the_expected_jobs():
    workflow = load_ci()
    assert set(workflow["jobs"]) >= {"python", "web", "ui", "docker", "paper"}


def test_ci_triggers_on_pull_requests():
    triggers = load_ci()[True] if True in load_ci() else load_ci()["on"]
    assert "pull_request" in triggers


def test_python_job_uses_a_postgres_service():
    python_job = load_ci()["jobs"]["python"]
    assert "postgres" in python_job["services"]
    assert python_job["services"]["postgres"]["image"].startswith("postgres")


def test_web_and_ui_jobs_run_checks():
    web = load_ci()["jobs"]["web"]["steps"]
    ui = load_ci()["jobs"]["ui"]["steps"]
    assert any("lint" in str(step.get("run", "")) for step in web)
    assert any("build" in str(step.get("run", "")) for step in web)
    assert any("build-storybook" in str(step.get("run", "")) for step in ui)


# ------------------------------------------------------------------------- e2e
@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
def test_compose_tools_profile_is_valid():
    completed = subprocess.run(
        ["docker", "compose", "--profile", "tools", "config", "--quiet"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
