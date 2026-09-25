"""Early-warning XR engagement/risk model.

For each learner the statements are split in time: the first half is an early
feature vector, the second half is the outcome. A learner whose later activity
falls below the cohort median is labelled elevated-risk, and a classifier learns
to flag that from early behaviour alone. This is the XR analogue of the Kalboard
support band — the same early-warning idea on XR behaviour, with no grade label.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from . import xr

#: Minimum early-window statements per learner to build a feature vector.
MIN_EARLY_EVENTS = 3
#: Predicted-probability cutoffs for the three risk bands.
ELEVATED_AT = 0.6
WATCH_AT = 0.4
#: Bands mapped onto the framework's support bands.
RISK_SUPPORT_BANDS = {
    "elevated": "priority-support",
    "watch": "monitor",
    "retained": "on-track",
}

_NON_FEATURE = ("learner", "school", "classroom")
_CACHE: dict[tuple[str, int], dict[str, Any]] = {}


def risk_band(probability: float) -> str:
    """Map a risk probability onto elevated/watch/retained."""
    if probability >= ELEVATED_AT:
        return "elevated"
    if probability >= WATCH_AT:
        return "watch"
    return "retained"


def build_dataset(
    statements: pd.DataFrame, min_early_events: int = MIN_EARLY_EVENTS
) -> tuple[pd.DataFrame, pd.Series]:
    """Return early-session features and a late-engagement risk label.

    The split is by calendar time, not by row count: splitting each learner's
    rows in half would make their early and late counts complementary and
    trivialise the label. Features come from the first half of the timeline; the
    label marks a learner *elevated-risk* when they had no activity in the final
    quarter of the timeline (they dropped out), versus *retained*.
    """
    if statements.empty:
        return pd.DataFrame(), pd.Series(dtype=int)

    early_cutoff = statements["timestamp"].quantile(0.5)
    late_cutoff = statements["timestamp"].quantile(0.75)
    early = statements[statements["timestamp"] < early_cutoff]
    tail = statements[statements["timestamp"] >= late_cutoff]

    early_counts = early.groupby("learner").size()
    keep = early_counts[early_counts >= min_early_events].index
    if len(keep) == 0:
        return pd.DataFrame(), pd.Series(dtype=int)

    features = xr.derive_learner_features(early[early["learner"].isin(keep)])
    columns = [column for column in features.columns if column not in _NON_FEATURE]
    features = features.set_index("learner")[columns]

    retained = set(tail["learner"].unique())
    labels = pd.Series(
        [0 if learner in retained else 1 for learner in features.index],
        index=features.index,
        dtype=int,
    )
    return features, labels


def _empty(reason: str, n: int = 0) -> dict[str, Any]:
    return {"available": False, "reason": reason, "learners": n}


def analyse(
    statements: pd.DataFrame,
    *,
    key: str = "",
    folds: int = 5,
    seed: int = 42,
) -> dict[str, Any]:
    """Train the early-warning model and return metrics and risk bands."""
    cache_key = (key, folds)
    if key and cache_key in _CACHE:
        return _CACHE[cache_key]

    features, labels = build_dataset(statements)
    if features.empty:
        return _empty("Not enough statements to build early and late windows.")
    if labels.nunique() < 2:
        return _empty("Only one engagement outcome in this cohort.", len(features))

    model = RandomForestClassifier(
        n_estimators=200, class_weight="balanced", random_state=seed, n_jobs=1
    )
    splits = int(min(folds, labels.value_counts().min()))
    splits = max(splits, 2)
    cv = StratifiedKFold(n_splits=splits, shuffle=True, random_state=seed)
    probabilities = cross_val_predict(
        model, features, labels, cv=cv, method="predict_proba"
    )[:, 1]

    model.fit(features, labels)
    importances = dict(
        sorted(
            zip(features.columns, model.feature_importances_, strict=True),
            key=lambda item: item[1],
            reverse=True,
        )[:10]
    )
    fitted = model.predict_proba(features)[:, 1]
    learners = [
        {
            "learner": str(learner),
            "risk": round(float(probability), 4),
            "band": risk_band(float(probability)),
        }
        for learner, probability in sorted(
            zip(features.index, fitted, strict=True),
            key=lambda item: item[1],
            reverse=True,
        )
    ]
    band_counts: dict[str, int] = {}
    for row in learners:
        band = str(row["band"])
        band_counts[band] = band_counts.get(band, 0) + 1

    payload = {
        "available": True,
        "n": int(len(features)),
        "positives": int(labels.sum()),
        "folds": splits,
        "roc_auc": round(float(roc_auc_score(labels, probabilities)), 4),
        "average_precision": round(
            float(average_precision_score(labels, probabilities)), 4
        ),
        "brier": round(float(brier_score_loss(labels, probabilities)), 4),
        "features": list(features.columns),
        "importances": {
            name: round(float(value), 4) for name, value in importances.items()
        },
        "bands": band_counts,
        "support_bands": RISK_SUPPORT_BANDS,
        "learners": learners[:25],
    }
    if key:
        _CACHE[cache_key] = payload
    return payload


def clear_cache() -> None:
    """Drop the cached payloads (used by tests)."""
    _CACHE.clear()
