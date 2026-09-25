"""ARETE XR dataset support.

The ARETE project (H2020, Scientific Data 2023, DOI 10.1038/s41597-023-02743-6)
published the raw xAPI statements from four augmented-reality education pilots
as Learning Locker CSV exports, licensed CC BY 4.0. This module parses a pilot,
derives per-learner session features, and produces descriptive engagement
trends over time.

It is the XR half of the framework's transfer demonstration: the same xAPI
schema the Kalboard prototype uses, a different feature set and no grade label.
Pilots are downloaded (not committed) and verified against a pinned SHA-256; see
``scripts/fetch_arete.py``.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import Settings, get_settings
from .xr_schema import LEARNER_SCHEMA, VERBS

ARETE_LICENCE = "CC BY 4.0"
ARETE_DOI = "10.1038/s41597-023-02743-6"


@dataclass(frozen=True)
class AretePilot:
    """One ARETE pilot and where to fetch its statements from."""

    name: str
    filename: str
    url: str
    sha256: str
    description: str


PILOTS: dict[str, AretePilot] = {
    "pbis": AretePilot(
        name="pbis",
        filename="xAPI_PBIS.csv",
        url="https://zenodo.org/records/7876959/files/xAPI_PBIS.csv",
        sha256="932735d5798c62dfbcdd259e8359fc9c1e6538045f336874a6c6cc92a226bde6",
        description=(
            "Positive Behaviour Intervention and Support: nine AR behavioural "
            "lessons across Dutch schools."
        ),
    ),
    # English Literacy, STEM Geometry, STEM Geography and LXD are added by the
    # 'all pilots' ticket.
}

_RENAME = {
    "timestamp": "timestamp",
    "actor name": "learner",
    "verb_display": "verb",
    "object name": "object",
    "result_raw": "result_raw",
    "result_response": "result_response",
}

_FREQ = {"D": "D", "DAY": "D", "W": "W", "WEEK": "W", "M": "M", "MONTH": "M"}


def get_pilot(name: str) -> AretePilot:
    """Return a pilot by name or raise ``ValueError``."""
    try:
        return PILOTS[name]
    except KeyError:
        known = ", ".join(sorted(PILOTS))
        raise ValueError(
            f"Unknown ARETE pilot '{name}'. Known pilots: {known}"
        ) from None


def pilot_path(pilot: AretePilot, settings: Settings | None = None) -> Path:
    """Return the on-disk location of a pilot's CSV."""
    settings = settings or get_settings()
    return settings.arete_raw_dir / pilot.filename


def available_pilots(settings: Settings | None = None) -> list[dict]:
    """Return pilot metadata with a download-availability flag."""
    settings = settings or get_settings()
    return [
        {
            "name": pilot.name,
            "filename": pilot.filename,
            "url": pilot.url,
            "licence": ARETE_LICENCE,
            "doi": ARETE_DOI,
            "description": pilot.description,
            "available": pilot_path(pilot, settings).exists(),
        }
        for pilot in PILOTS.values()
    ]


def sha256_of(path: Path) -> str:
    """Return the hex SHA-256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_statements(path: Path | str) -> pd.DataFrame:
    """Read a Learning Locker CSV export into a tidy statement frame."""
    frame = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    frame = frame[[*_RENAME]].rename(columns=_RENAME)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
    frame["verb"] = frame["verb"].astype("string").str.strip().str.lower()
    frame["learner"] = frame["learner"].astype("string").str.strip()
    frame["object"] = frame["object"].astype("string").str.strip()
    frame["result_raw"] = pd.to_numeric(frame["result_raw"], errors="coerce")
    return frame.dropna(subset=["timestamp", "learner"]).reset_index(drop=True)


def load_pilot(
    name: str,
    settings: Settings | None = None,
    path: Path | str | None = None,
) -> tuple[pd.DataFrame, AretePilot]:
    """Return ``(tidy statements, pilot)`` for a downloaded pilot."""
    pilot = get_pilot(name)
    source = Path(path) if path else pilot_path(pilot, settings)
    if not source.exists():
        raise FileNotFoundError(
            f"{pilot.filename} not found at {source}. Run `make fetch-arete` "
            f"(or `uv run python scripts/fetch_arete.py {pilot.name}`)."
        )
    return parse_statements(source), pilot


def _split_actor(actor: str) -> tuple[str, str]:
    """Split ``SCHOOLNL1-klas2-rose`` into school and classroom."""
    parts = actor.split("-", 2)
    if len(parts) == 3:
        return parts[0], parts[1]
    return actor, ""


def derive_learner_features(statements: pd.DataFrame) -> pd.DataFrame:
    """Aggregate statements into one validated engagement row per learner."""
    frame = statements.copy()
    frame["day"] = frame["timestamp"].dt.date

    base = frame.groupby("learner").agg(
        events=("verb", "size"),
        active_days=("day", "nunique"),
        distinct_verbs=("verb", "nunique"),
        distinct_objects=("object", "nunique"),
        responses=("result_raw", lambda values: int(values.notna().sum())),
        first_seen=("timestamp", "min"),
        last_seen=("timestamp", "max"),
    )

    verb_counts = frame.groupby(["learner", "verb"]).size().unstack(fill_value=0)
    for verb in VERBS:
        if verb not in verb_counts.columns:
            verb_counts[verb] = 0
    verb_counts = verb_counts[VERBS].add_prefix("verb_")

    features = base.join(verb_counts)
    features["span_days"] = (
        features["last_seen"] - features["first_seen"]
    ).dt.total_seconds() / 86400.0
    features["events_per_active_day"] = features["events"] / features[
        "active_days"
    ].clip(lower=1)

    parts = features.index.to_series().map(_split_actor)
    features["school"] = [part[0] for part in parts]
    features["classroom"] = [part[1] for part in parts]
    features = features.reset_index()

    columns = [
        "learner",
        "school",
        "classroom",
        "events",
        "active_days",
        "distinct_verbs",
        "distinct_objects",
        "responses",
        "span_days",
        "events_per_active_day",
        *[f"verb_{verb}" for verb in VERBS],
    ]
    return features[columns]


def validate_features(features: pd.DataFrame) -> pd.DataFrame:
    """Validate the derived learner frame against the XR schema."""
    return LEARNER_SCHEMA.validate(features, lazy=True)


def engagement_trends(statements: pd.DataFrame, freq: str = "W") -> dict:
    """Summarise engagement over time for a statement frame."""
    offset = _FREQ.get(freq.upper())
    if offset is None:
        raise ValueError(f"Unsupported frequency '{freq}'. Use D, W or M.")

    frame = statements.copy()
    frame["period"] = (
        frame["timestamp"]
        .dt.tz_convert("UTC")
        .dt.tz_localize(None)
        .dt.to_period(offset)
        .dt.start_time
    )
    timeline = (
        frame.groupby("period")
        .agg(events=("verb", "size"), active_learners=("learner", "nunique"))
        .reset_index()
        .sort_values("period")
    )
    verb_counts = frame["verb"].value_counts()
    top_objects = frame["object"].dropna().value_counts().head(10)

    return {
        "events": int(len(frame)),
        "learners": int(frame["learner"].nunique()),
        "first_seen": frame["timestamp"].min().isoformat(),
        "last_seen": frame["timestamp"].max().isoformat(),
        "period_start": [period.isoformat() for period in timeline["period"]],
        "events_by_period": [int(value) for value in timeline["events"]],
        "active_learners_by_period": [
            int(value) for value in timeline["active_learners"]
        ],
        "verb_counts": {str(key): int(value) for key, value in verb_counts.items()},
        "top_objects": [
            {"name": str(name), "count": int(count)}
            for name, count in top_objects.items()
        ],
    }
