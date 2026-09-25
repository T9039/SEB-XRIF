"""Adapters folding the ARETE XR pilots onto the dataset seam.

The ARETE exports carry no grade outcome, so the target here is **derived**: a
learner is labelled ``elevated`` when they had no activity in the final quarter
of the pilot timeline, and ``retained`` otherwise. That is an engagement /
drop-off signal, not an academic performance band, and it is labelled as such.
"""

from __future__ import annotations

from .. import xr, xr_risk
from ..config import Settings, get_settings
from .base import Dataset, DatasetAdapter

TARGET = "dropout_risk"
_LABELS = {0: "retained", 1: "elevated"}


class AreteAdapter(DatasetAdapter):
    """Base for the ARETE pilots; subclasses set ``name`` and ``pilot``."""

    pilot: str = ""

    def load(self, settings: Settings | None = None) -> Dataset:
        settings = settings or get_settings()
        statements, meta = xr.load_pilot(self.pilot, settings)
        features, labels = xr_risk.build_dataset(statements)
        if features.empty:
            raise ValueError(
                f"{meta.filename} has no usable cohort for an early/late split."
            )

        frame = features.reset_index()
        frame[TARGET] = [_LABELS[int(value)] for value in labels]
        return Dataset(
            name=self.name,
            description=(
                f"{meta.description} Target is derived drop-off risk "
                "(elevated vs retained), not an academic band."
            ),
            source=self.name,
            frame=frame,
            features=list(features.columns),
            target=TARGET,
            class_labels=["retained", "elevated"],
        )


class AretePbisAdapter(AreteAdapter):
    name = "arete-pbis"
    pilot = "pbis"


class AreteEnglishLiteracyAdapter(AreteAdapter):
    name = "arete-english-literacy"
    pilot = "english-literacy"


class AreteStemGeometryAdapter(AreteAdapter):
    name = "arete-stem-geometry"
    pilot = "stem-geometry"


class AreteStemGeographyAdapter(AreteAdapter):
    name = "arete-stem-geography"
    pilot = "stem-geography"


class AreteLxdAdapter(AreteAdapter):
    name = "arete-lxd"
    pilot = "lxd"
