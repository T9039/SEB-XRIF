"""Pandera schema for the ARETE-derived per-learner engagement frame.

The frame is one row per learner: session-level behaviour derived from their
xAPI statements. It is the XR analogue of the Kalboard feature table and the
input to the engagement/risk work.

The five ARETE pilots use different verbs and locales, so the frame does not
carry one column per raw verb. Raw verbs are mapped to a small, stable set of
behaviour classes, which keeps the schema identical across pilots.
"""

from __future__ import annotations

try:  # pandera >= 0.21 exposes the pandas backend explicitly
    from pandera.pandas import Check, Column, DataFrameSchema
except ImportError:  # pragma: no cover - fallback for older pandera
    from pandera import Check, Column, DataFrameSchema

import re

#: Raw verbs (lowercased) grouped into stable behaviour classes.
VERB_CLASSES: dict[str, set[str]] = {
    "interaction": {
        "selected",
        "placed",
        "found",
        "interacted",
        "picked_up",
        "opened",
        "located",
        "actionpredicate_drawing",
    },
    "progress": {
        "started",
        "launched",
        "joined",
        "completed",
        "log_in",
        "return_to_app",
        "pause_app",
        "enabled",
        "module_status",
    },
    "assessment": {"responded", "answered", "attempted"},
    "content": {
        "accessed",
        "consumed",
        "read",
        "viewed",
        "watched",
        "listened_to",
        "focused_on",
        "noticed",
        "measured",
        "met",
        "experienced",
        "followed",
    },
    "disengagement": {
        "skipped",
        "stopped_following",
        "left",
        "exit",
        "unplugged",
    },
}

#: Feature column names derived from the behaviour classes.
VERB_FEATURES = [f"verb_{name}" for name in (*VERB_CLASSES, "other")]

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalise_verb(verb: str) -> str:
    """Lowercase a raw verb and collapse separators to underscores."""
    return _NON_ALNUM.sub("_", str(verb).strip().lower()).strip("_")


def verb_class(verb: str) -> str:
    """Return the behaviour class for a raw verb, or ``"other"``."""
    normalised = normalise_verb(verb)
    for name, members in VERB_CLASSES.items():
        if normalised in members:
            return name
    return "other"


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
        **{feature: Column(int, Check.ge(0)) for feature in VERB_FEATURES},
    },
    strict=True,
    coerce=True,
)
