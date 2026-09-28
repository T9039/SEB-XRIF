"""Adapter for a tabular source registered with an explicit column mapping.

This is the "adaptation" path for a plain table downloaded from the internet:
a CSV with a target column and feature columns, mapped onto the framework's
Dataset contract. Nothing is fabricated — the mapping names existing columns,
and if a required column is absent the load fails rather than inventing values.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import Settings, get_settings
from .base import Dataset, DatasetAdapter


class TableAdapter(DatasetAdapter):
    """Reads a tabular source using a declared feature/target mapping."""

    name = "table"

    def __init__(
        self,
        *,
        name: str,
        path: Path | str,
        target: str,
        features: list[str],
        categorical: list[str] | None = None,
        numeric: list[str] | None = None,
        description: str = "",
    ) -> None:
        self.name = name
        self.path = Path(path)
        self.target = target
        self.features = list(features)
        self.categorical = list(categorical or [])
        self.numeric = list(
            numeric or [f for f in self.features if f not in self.categorical]
        )
        self.description = description

    def load(self, settings: Settings | None = None) -> Dataset:
        settings = settings or get_settings()
        if not self.path.exists():
            raise ValueError(f"Table source '{self.name}' is missing {self.path}.")

        frame = pd.read_csv(self.path)
        required = [*self.features, self.target]
        missing = [column for column in required if column not in frame.columns]
        if missing:
            raise ValueError(
                f"Table source '{self.name}' is missing columns: {missing}."
            )
        if frame[self.target].isna().any():
            raise ValueError(
                f"Table source '{self.name}' has missing values in target "
                f"'{self.target}'."
            )

        labels = sorted(str(value) for value in frame[self.target].unique())
        return Dataset(
            name=self.name,
            description=self.description,
            source=self.name,
            frame=frame,
            features=self.features,
            target=self.target,
            class_labels=labels,
            categorical=self.categorical,
            numeric=self.numeric,
        )
