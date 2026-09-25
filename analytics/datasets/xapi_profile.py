"""Adapter for any source whose xAPI statements follow the framework profile.

This is the no-code ingest path: a producer exports the framework's xAPI profile
(a ``registered`` statement carrying demographics, ``progressed`` statements
carrying behavioural scores, and a ``completed`` statement carrying the target)
from their LRS, and drops the file in. The profile itself is the contract, so no
per-source adapter is written.
"""

from __future__ import annotations

from pathlib import Path

from ..config import Settings, get_settings
from ..schema import BEHAVIOURAL, CATEGORICAL, SCHEMA
from ..xapi import frame_from_statements, read_statements
from .base import Dataset, DatasetAdapter


class XapiProfileAdapter(DatasetAdapter):
    """Reads a profile-conformant statements file into a canonical dataset."""

    name = "xapi-profile"
    description = (
        "Any xAPI source that follows the framework profile (registered / "
        "progressed / completed statements)."
    )

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = path

    def load(self, settings: Settings | None = None) -> Dataset:
        settings = settings or get_settings()
        source_path = Path(self.path) if self.path else settings.statements_path
        statements = read_statements(source_path)
        frame = frame_from_statements(statements)

        features = [*CATEGORICAL, *BEHAVIOURAL]
        if frame.empty or frame[features].isna().all(axis=None):
            raise ValueError(
                f"{source_path} does not contain profiles with demographics and "
                "behavioural statements."
            )
        if not frame[settings.target].notna().any():
            raise ValueError(
                f"{source_path} carries no '{settings.target}' target; the "
                "framework profile needs a completed statement with the target."
            )

        validated = SCHEMA.validate(frame, lazy=True)
        return Dataset(
            name=self.name,
            description=self.description,
            source="xapi-profile",
            frame=validated,
            features=features,
            target=settings.target,
            class_labels=list(settings.class_labels),
        )
