"""The dataset-adapter seam.

An adapter turns one source of learner records into the canonical feature frame
(see ``analytics.schema``) plus a provenance label. The analytics core never
reads a source directly; it asks the registry for the configured adapter, so a
new xAPI source is a new adapter rather than a branch in the pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ..config import Settings


class DatasetAdapter(ABC):
    """Maps one raw source onto the canonical learner frame."""

    name: str
    description: str = ""

    @abstractmethod
    def load(self, settings: Settings) -> tuple[pd.DataFrame, str]:
        """Return ``(validated canonical frame, source label)``."""
