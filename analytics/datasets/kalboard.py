"""Adapter for the bundled xAPI Educational Mining Dataset (Kalboard 360).

The records are primary and secondary school LMS data (non-XR). They prototype
the analytics layer; XR sources plug in through their own adapters.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import Settings, get_settings
from ..schema import SCHEMA
from .base import Dataset, DatasetAdapter


class KalboardAdapter(DatasetAdapter):
    """K-12, non-XR LMS data used to prototype the analytics layer."""

    name = "kalboard"
    description = "xAPI Educational Mining Dataset (Kalboard 360); K-12, non-XR."

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate against the canonical schema, returning a coerced copy."""
        return SCHEMA.validate(df, lazy=True)

    def load_raw(
        self, path: Path | str | None = None, settings: Settings | None = None
    ) -> pd.DataFrame:
        """Load the raw learner table from CSV."""
        settings = settings or get_settings()
        csv_path = Path(path) if path else settings.raw_path
        return pd.read_csv(csv_path)

    def read_learners(
        self, settings: Settings | None = None, prefer_db: bool = True
    ) -> tuple[pd.DataFrame, str]:
        """Return a validated frame, preferring the database when populated."""
        settings = settings or get_settings()
        if prefer_db:
            try:
                from ..db import get_engine, learners_frame

                frame = learners_frame(get_engine())
                if not frame.empty:
                    return self.validate(frame), "database"
            except Exception:  # noqa: BLE001 - fall back to the CSV seed
                pass
        return self.validate(self.load_raw(settings=settings)), "csv"

    def load(self, settings: Settings | None = None) -> Dataset:
        settings = settings or get_settings()
        if settings.data_source == "db":
            frame, source = self.read_learners(settings, prefer_db=True)
        else:
            frame, source = self.validate(self.load_raw(settings=settings)), "csv"
        return Dataset(
            name=self.name,
            description=self.description,
            source=source,
            frame=frame,
            features=list(settings.feature_columns),
            target=settings.target,
            class_labels=list(settings.class_labels),
        )
