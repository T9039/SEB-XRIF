"""Feature and end-to-end tests for the docker-compose infrastructure."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSE = REPO_ROOT / "docker-compose.yml"
INIT_SQL = REPO_ROOT / "docker" / "postgres" / "init-lrsql.sql"


def load_compose() -> dict:
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))


# --------------------------------------------------------------------- feature
def test_lrsql_service_is_configured():
    services = load_compose()["services"]
    assert "lrsql" in services

    lrsql = services["lrsql"]
    assert lrsql["image"].startswith("yetanalytics/lrsql")
    assert lrsql["command"] == ["/lrsql/bin/run_postgres.sh"]

    env = lrsql["environment"]
    assert env["LRSQL_DB_NAME"] == "lrsql_db"
    assert env["LRSQL_DB_HOST"] == "db"
    assert str(env["LRSQL_ENABLE_CLAMAV"]).lower() == "false"
    assert "8081:8080" in lrsql["ports"]


def test_db_mounts_lrsql_init_script():
    services = load_compose()["services"]
    mounts = services["db"]["volumes"]
    assert any("init-lrsql.sql" in str(mount) for mount in mounts)
    assert INIT_SQL.exists()
    assert "lrsql_db" in INIT_SQL.read_text(encoding="utf-8")


def test_api_knows_the_lrs_endpoint():
    env = load_compose()["services"]["api"]["environment"]
    assert env["LRS_ENDPOINT"] == "http://lrsql:8080/xapi"
    assert "LRS_KEY" in env and "LRS_SECRET" in env


def test_storybook_is_behind_the_tools_profile():
    services = load_compose()["services"]
    assert "storybook" in services
    assert "tools" in services["storybook"]["profiles"]


# ------------------------------------------------------------------------- e2e
@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
def test_compose_config_is_valid():
    completed = subprocess.run(
        ["docker", "compose", "config", "--quiet"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
