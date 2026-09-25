"""Configuration loading for the analytics layer.

Reads ``analytics/config.yaml`` once and exposes a frozen ``Settings`` object.
All paths in the config are resolved relative to the repository root so the
pipeline is location independent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
CONFIG_PATH = PACKAGE_DIR / "config.yaml"


@dataclass(frozen=True)
class Settings:
    """Typed view over the analytics configuration."""

    seed: int
    test_size: float
    cv_folds: int
    target: str
    class_labels: list[str]
    categorical: list[str]
    behavioural: list[str]
    random_forest: dict[str, Any]
    paths: dict[str, str]
    repo_root: Path
    n_jobs: int = 1
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"
    mlflow_experiment: str = "seb-xrif"
    mlflow_registered_model: str = "seb-xrif-random-forest"
    database_url: str = "sqlite:///sebxrif.db"
    data_source: str = "csv"
    lrs_endpoint: str = "http://localhost:8081/xapi"
    lrs_key: str = "seb-xrif-lrs"
    lrs_secret: str = "seb-xrif-secret"
    dataset: str = "kalboard"
    support_bands: dict[str, str] = field(
        default_factory=lambda: {
            "L": "priority-support",
            "M": "monitor",
            "H": "on-track",
        }
    )
    decision_thresholds: dict[str, float] = field(default_factory=dict)

    def resolve_database_url(self) -> str:
        """Return the application database URL, preferring the environment."""
        import os

        return os.environ.get("DATABASE_URL", self.database_url)

    def tracking_uri(self) -> str:
        """Return the MLflow tracking URI, preferring the environment."""
        import os

        return os.environ.get("MLFLOW_TRACKING_URI", self.mlflow_tracking_uri)

    def resolve(self, key: str) -> Path:
        """Resolve a configured path relative to the repository root."""
        return (self.repo_root / self.paths[key]).resolve()

    @property
    def raw_path(self) -> Path:
        return self.resolve("raw")

    @property
    def processed_path(self) -> Path:
        return self.resolve("processed")

    @property
    def model_path(self) -> Path:
        return self.resolve("model")

    @property
    def metadata_path(self) -> Path:
        return self.resolve("metadata")

    @property
    def run_path(self) -> Path:
        """Volatile run provenance, kept out of the reproducible artifact."""
        return self.metadata_path.with_name("model.run.json")

    @property
    def reports_dir(self) -> Path:
        return self.resolve("reports")

    @property
    def arete_raw_dir(self) -> Path:
        return self.resolve("arete_raw")

    @property
    def feature_columns(self) -> list[str]:
        return [*self.categorical, *self.behavioural]


@lru_cache(maxsize=1)
def get_settings(config_path: Path | None = None) -> Settings:
    """Load and cache the analytics settings."""
    path = Path(config_path) if config_path else CONFIG_PATH
    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return Settings(repo_root=REPO_ROOT, **raw)
