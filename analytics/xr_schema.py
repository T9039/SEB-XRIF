"""Pandera schema for the ARETE-derived per-learner engagement frame.

The frame is one row per learner: session-level behaviour derived from their
xAPI statements. It is the XR analogue of the Kalboard feature table and the
input to the engagement/risk work.
"""

from __future__ import annotations

try:  # pandera >= 0.21 exposes the pandas backend explicitly
    from pandera.pandas import Check, Column, DataFrameSchema
except ImportError:  # pragma: no cover - fallback for older pandera
    from pandera import Check, Column, DataFrameSchema

#: Verbs observed across the ARETE pilots (Learning Locker ``verb_display``).
VERBS = [
    "accessed",
    "completed",
    "consumed",
    "found",
    "joined",
    "left",
    "placed",
    "read",
    "responded",
    "selected",
    "skipped",
    "started",
]

LEARNER_SCHEMA = DataFrameSchema(
    {
        "learner": Column(str),
        "school": Column(str),
        "classroom": Column(str),
        "events": Column(int, Check.ge(1)),
        "active_days": Column(int, Check.ge(1)),
        "distinct_verbs": Column(int, Check.ge(1)),
        "distinct_objects": Column(int, Check.ge(0)),
        "responses": Column(int, Check.ge(0)),
        "span_days": Column(float, Check.ge(0)),
        "events_per_active_day": Column(float, Check.gt(0)),
        **{f"verb_{verb}": Column(int, Check.ge(0)) for verb in VERBS},
    },
    strict=True,
    coerce=True,
)
