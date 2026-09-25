"""ARETE XR dataset support.

The ARETE project (H2020, Scientific Data 2023, DOI 10.1038/s41597-023-02743-6)
published the raw xAPI statements from four augmented-reality education pilots
(five CSV files) as Learning Locker exports, licensed CC BY 4.0. This module
parses a pilot, derives per-learner session features, and produces descriptive
engagement trends over time.

It is the XR half of the framework's transfer demonstration: the same xAPI
schema the Kalboard prototype uses, a different feature set and no grade label.
Pilots are downloaded (not committed) and verified against a pinned SHA-256; see
``scripts/fetch_arete.py``.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import Settings, get_settings
from .xr_schema import LEARNER_SCHEMA, VERB_FEATURES, verb_class

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
    "english-literacy": AretePilot(
        name="english-literacy",
        filename="EnglishLiteracy-Anonymized.csv",
        url=("https://zenodo.org/records/7876947/files/EnglishLiteracy-Anonymized.csv"),
        sha256="5c891a5b64b6334a5d94c9d3ac710817a9005f1468deeb420cac638f6e55c942",
        description=("English literacy AR modules in primary and secondary schools."),
    ),
    "stem-geometry": AretePilot(
        name="stem-geometry",
        filename="STEMGeometry.csv",
        url="https://zenodo.org/records/7877072/files/STEMGeometry.csv",
        sha256="a1758cae5e75466fa0652f6965c783addd66aea25cffa79acca8fa84ccd3cba8",
        description="STEM geometry AR activities in European classrooms.",
    ),
    "stem-geography": AretePilot(
        name="stem-geography",
        filename="STEMGeography.csv",
        url="https://zenodo.org/records/7877072/files/STEMGeography.csv",
        sha256="7db90cbd775bab9298ab4776e6d1b529281cbb4892c5783be11dd8e26ba562bc",
        description="STEM geography AR activities in European classrooms.",
    ),
    "lxd": AretePilot(
        name="lxd",
        filename="LXD.csv",
        url="https://zenodo.org/records/8009365/files/LXD.csv",
        sha256="55a76950e76043b94ee59b6c5a934ab5df09d5ccd6c1f7c9b70719e9a26fea00",
        description=(
            "Learning Experience Design: teachers authoring AR learning "
            "resources with the ARETE toolkit."
        ),
    ),
}

_FREQ = {"D": "D", "DAY": "D", "W": "W", "WEEK": "W", "M": "M", "MONTH": "M"}

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_FIRST_NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")

#: Flat columns, normalised, mapped to the canonical names this module emits.
_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "timestamp": ("timestamp",),
    "learner": ("actor_name", "actor"),
    "verb_id": ("verb_id",),
    "verb": ("verb_display", "verb"),
    "object_id": ("object_id",),
    "object": ("object_name", "object"),
    "result": ("result",),
    "result_response": ("result_response",),
    "result_raw": ("result_raw",),
    "language": ("language",),
}


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


def _normalise_key(name: object) -> str:
    return _NON_ALNUM.sub("_", str(name).strip().lower()).strip("_")


def _detect_sep(path: Path | str) -> str:
    """Return the delimiter of a Learning Locker export (``;`` or ``,``)."""
    sample = Path(path).read_bytes()[:8192].decode("utf-8-sig", errors="replace")
    return ";" if sample.count(";") > sample.count(",") else ","


def _display_text(value: object) -> object:
    """Extract the text from a Learning Locker display dict-string."""
    if not isinstance(value, str):
        return value
    match = re.search(
        r"['\"][a-zA-Z]{2}-[a-zA-Z]{2}['\"]\s*:\s*['\"]([^'\"]*)['\"]", value
    )
    if match:
        return match.group(1).strip()
    return value.strip()


def _parse_json(value: str) -> dict | None:
    """Best-effort parse of a Learning Locker result blob."""
    text = value.strip()
    if not text:
        return None
    for candidate in (text, text.replace("&46;", ".").replace("&quot;", '"')):
        try:
            parsed = json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            try:
                parsed = ast.literal_eval(candidate)
            except (ValueError, SyntaxError):
                continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _to_float(value: object) -> float:
    """Pull the first number out of a value, tolerating units and commas."""
    if isinstance(value, (int, float)):
        return float(value)
    match = _FIRST_NUMBER.search(str(value).replace(",", "."))
    return float(match.group()) if match else float("nan")


def _result_number(value: object) -> float:
    """Derive a numeric response from a Learning Locker result field."""
    if not isinstance(value, str):
        return float("nan")
    parsed = _parse_json(value)
    if parsed is None:
        return float("nan")
    score = parsed.get("score")
    if isinstance(score, dict) and "raw" in score:
        return _to_float(score["raw"])
    for flag in ("success", "completion"):
        if flag in parsed:
            return 1.0 if parsed[flag] else 0.0
    extensions = parsed.get("extensions")
    if isinstance(extensions, dict):
        for key, measured in extensions.items():
            if "measuredValue" in str(key):
                return _to_float(measured)
    return float("nan")


def _column_lookup(columns: list[str]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for column in columns:
        lookup[_normalise_key(column)] = column
    return lookup


def _pick(lookup: dict[str, str], canonical: str) -> str | None:
    for alias in _COLUMN_ALIASES[canonical]:
        if alias in lookup:
            return lookup[alias]
    return None


def parse_statements(path: Path | str) -> pd.DataFrame:
    """Read any ARETE Learning Locker CSV export into a tidy frame.

    Handles the differences between pilots: ``,``/``;`` delimiters, a UTF-8 BOM,
    ``actor``/``actor name`` and ``verb id``/``verb display`` spellings,
    dict-string displays, trailing empty columns, and the various result shapes
    (``score.raw``, ``success``, ``completion``, measured values).
    """
    sep = _detect_sep(path)
    raw = pd.read_csv(path, sep=sep, encoding="utf-8-sig", dtype=str)
    raw.columns = [str(column).strip() for column in raw.columns]
    raw = raw.loc[
        :,
        [
            column
            for column in raw.columns
            if column and not _normalise_key(column).startswith("unnamed")
        ],
    ]
    lookup = _column_lookup(list(raw.columns))

    out = pd.DataFrame(index=raw.index)
    timestamp_col = _pick(lookup, "timestamp")
    learner_col = _pick(lookup, "learner")
    verb_col = _pick(lookup, "verb")
    object_col = _pick(lookup, "object")
    if None in (timestamp_col, learner_col, verb_col, object_col):
        raise ValueError(
            "ARETE export is missing one of timestamp/actor/verb/object columns."
        )

    out["timestamp"] = pd.to_datetime(raw[timestamp_col], errors="coerce", utc=True)
    out["learner"] = raw[learner_col].astype("string").str.strip()
    out["verb"] = raw[verb_col].map(_display_text).astype("string").str.strip()
    out["verb"] = out["verb"].str.lower()
    out["object"] = raw[object_col].map(_display_text).astype("string").str.strip()

    numbers = pd.Series(np.nan, index=raw.index, dtype="float64")
    result_col = _pick(lookup, "result")
    if result_col is not None:
        numbers = raw[result_col].map(_result_number).astype("float64")
    raw_col = _pick(lookup, "result_raw")
    if raw_col is not None:
        explicit = pd.to_numeric(raw[raw_col], errors="coerce")
        numbers = explicit.where(explicit.notna(), numbers)
    out["result_raw"] = numbers

    response_col = _pick(lookup, "result_response")
    out["result_response"] = (
        raw[response_col].astype("string") if response_col else pd.NA
    )
    language_col = _pick(lookup, "language")
    out["language"] = raw[language_col].astype("string") if language_col else pd.NA

    return out.dropna(subset=["timestamp", "learner"]).reset_index(drop=True)


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
    """Split the PBIS ``SCHOOLNL1-klas2-rose`` form into school and classroom.

    Other pilots use UUIDs or numeric ids, so anything that is not exactly two
    hyphens is returned as a school-less learner.
    """
    if actor.count("-") == 2:
        school, classroom, _ = actor.split("-", 2)
        return school, classroom
    return "", ""


def derive_learner_features(statements: pd.DataFrame) -> pd.DataFrame:
    """Aggregate statements into one validated engagement row per learner."""
    frame = statements.copy()
    frame["day"] = frame["timestamp"].dt.date
    frame["verb_class"] = frame["verb"].map(verb_class)

    base = frame.groupby("learner").agg(
        events=("verb", "size"),
        active_days=("day", "nunique"),
        distinct_verbs=("verb", "nunique"),
        distinct_objects=("object", "nunique"),
        responses=("result_raw", lambda values: int(values.notna().sum())),
        first_seen=("timestamp", "min"),
        last_seen=("timestamp", "max"),
    )

    class_counts = frame.groupby(["learner", "verb_class"]).size().unstack(fill_value=0)
    for feature in VERB_FEATURES:
        name = feature.removeprefix("verb_")
        if name not in class_counts.columns:
            class_counts[name] = 0
    class_counts = class_counts[
        [feature.removeprefix("verb_") for feature in VERB_FEATURES]
    ].add_prefix("verb_")

    features = base.join(class_counts)
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
        *VERB_FEATURES,
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
    frame["verb_class"] = frame["verb"].map(verb_class)
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
    class_counts = frame["verb_class"].value_counts()
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
        "verb_class_counts": {
            str(key): int(value) for key, value in class_counts.items()
        },
        "top_objects": [
            {"name": str(name), "count": int(count)}
            for name, count in top_objects.items()
        ],
    }
