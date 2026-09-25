"""API settings, loaded from the environment with sensible defaults.

Paths default to the repository layout so the service runs from a checkout
with no configuration. Override with ``SEBXRIF_*`` environment variables or a
``.env`` file.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[1]


class ApiSettings(BaseSettings):
    """Runtime configuration for the SEB-XRIF service."""

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="SEBXRIF_", extra="ignore"
    )

    model_path: Path = REPO_ROOT / "models" / "model.joblib"
    metadata_path: Path = REPO_ROOT / "models" / "model.meta.json"
    run_path: Path = REPO_ROOT / "models" / "model.run.json"
    shap_path: Path = REPO_ROOT / "models" / "shap.json"
    raw_data_path: Path = REPO_ROOT / "data" / "raw" / "xAPI-Edu-Data.csv"

    # Model source: "local" (joblib artifact) or "registry" (MLflow registry).
    model_source: str = "local"
    registered_model: str = "seb-xrif-random-forest"
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"

    target: str = "Class"
    class_labels: list[str] = Field(default_factory=lambda: ["L", "M", "H"])


@lru_cache(maxsize=1)
def get_api_settings() -> ApiSettings:
    """Return the cached API settings."""
    return ApiSettings()
