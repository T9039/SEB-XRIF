"""Longitudinal T0/T1/T2 evaluation protocol.

Every SEB-XRIF adopter measures the same three time points: T0 baseline before
the XR module, T1 immediately after, and T2 one semester later with no
re-teaching. This module turns three score vectors into the reported effect
sizes so the protocol cannot drift between studies.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from ..effect_size import cohens_d

TIME_POINTS = ("T0", "T1", "T2")

#: Reference benchmarks used in the technical specification, section 7.
SUS_BENCHMARK = 76.6
COHEN_D_BENCHMARK = 0.936
COHEN_THRESHOLDS = {"small": 0.2, "medium": 0.5, "large": 0.8}


def validate_time_point(time_point: str) -> str:
    """Return the time point if valid, else raise."""
    if time_point not in TIME_POINTS:
        raise ValueError(f"time_point must be one of {TIME_POINTS}")
    return time_point


@dataclass(frozen=True)
class Measurement:
    """A single learner score at one time point."""

    learner_id: str
    time_point: str
    score: float

    def __post_init__(self) -> None:
        validate_time_point(self.time_point)


@dataclass(frozen=True)
class TimePointSummary:
    """Descriptive and effect-size summary for one comparison."""

    n: int
    mean: float
    gain: float
    cohens_d: float


def _summary(group: Sequence[float], baseline: Sequence[float]) -> TimePointSummary:
    if len(group) != len(baseline):
        raise ValueError("all time points must have the same number of learners")
    mean = float(np.mean(group))
    base = float(np.mean(baseline))
    return TimePointSummary(
        n=len(group),
        mean=mean,
        gain=float(mean - base),
        cohens_d=float(cohens_d(group, baseline, paired=True)),
    )


def summarise(
    t0: Sequence[float],
    t1: Sequence[float],
    t2: Sequence[float] | None = None,
) -> dict:
    """Summarise immediate and (optionally) delayed learning outcomes.

    Args:
        t0: baseline scores.
        t1: immediate post-intervention scores.
        t2: optional delayed post scores, one semester later.
    """
    immediate = _summary(t1, t0)
    result: dict = {
        "n": immediate.n,
        "mean_t0": float(np.mean(t0)),
        "mean_t1": immediate.mean,
        "gain_immediate": immediate.gain,
        "d_immediate": immediate.cohens_d,
    }
    if t2 is not None:
        delayed = _summary(t2, t0)
        decay = _summary(t2, t1)
        denom = immediate.gain
        result.update(
            {
                "mean_t2": delayed.mean,
                "gain_delayed": delayed.gain,
                "d_delayed": delayed.cohens_d,
                "decay_t2_t1": decay.gain,
                "d_decay": decay.cohens_d,
                "retention_ratio": (
                    float(delayed.gain / denom) if denom != 0 else None
                ),
            }
        )
    return result
