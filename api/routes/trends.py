"""Behavioural trend route for dashboard charts.

Aggregates the raw learner table directly, so trends are available even before
a model has been trained.
"""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException

from ..config import get_api_settings

router = APIRouter(tags=["analytics"])

_BEHAVIOURAL = ["raisedhands", "VisITedResources", "AnnouncementsView", "Discussion"]


@router.get("/trends")
def trends() -> dict:
    """Return class counts and mean behaviour per tier."""
    settings = get_api_settings()
    if not settings.raw_data_path.exists():
        raise HTTPException(status_code=503, detail="Raw dataset not found.")

    df = pd.read_csv(settings.raw_data_path)
    target = settings.target

    class_counts = {
        str(label): int(count) for label, count in df[target].value_counts().items()
    }
    behaviour_by_class = (
        df.groupby(target)[_BEHAVIOURAL].mean().round(2).to_dict(orient="index")
    )
    by_topic = (
        df.groupby(["Topic", target])
        .size()
        .unstack(fill_value=0)
        .to_dict(orient="index")
    )

    return {
        "total_records": int(len(df)),
        "class_counts": class_counts,
        "behaviour_by_class": {
            str(label): {k: float(v) for k, v in values.items()}
            for label, values in behaviour_by_class.items()
        },
        "by_topic": {
            str(topic): {str(k): int(v) for k, v in counts.items()}
            for topic, counts in by_topic.items()
        },
    }
