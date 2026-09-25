"""The dataset-adapter seam.

An adapter turns one source of learner records into a canonical :class:`Dataset`:
the feature frame plus the metadata the pipeline needs — which columns are
features, which column (if any) is the target, and the class labels. The
analytics core never reads a source directly; it asks the registry for the
configured adapter, so a new xAPI source is a new adapter rather than a branch
in the pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ..config import Settings


@dataclass(frozen=True)
class Dataset:
    """A source's canonical frame plus the metadata the pipeline needs."""

    name: str
    description: str
    source: str
    frame: pd.DataFrame
    features: list[str]
    target: str | None = None
    class_labels: list[str] = field(default_factory=list)
    metric: str = "f1_macro"
    categorical: list[str] = field(default_factory=list)
    numeric: list[str] = field(default_factory=list)

    @property
    def supervised(self) -> bool:
        """True when the dataset declares a target to predict."""
        return self.target is not None and self.target in self.frame.columns


class DatasetAdapter(ABC):
    """Maps one raw source onto a canonical :class:`Dataset`."""

    name: str
    description: str = ""

    @abstractmethod
    def load(self, settings: Settings) -> Dataset:
        """Return the canonical dataset for this source."""
