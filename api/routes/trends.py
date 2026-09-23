"""Behavioural trend route for dashboard charts.

Reads the application database when it holds learners, and falls back to the
bundled CSV seed otherwise. The response reports which source was used.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from analytics.config import get_settings as get_analytics_settings
from analytics.data import read_learners

router = APIRouter(tags=["analytics"])

_BEHAVIOURAL = ["raisedhands", "VisITedResources", "AnnouncementsView", "Discussion"]


@router.get("/trends")
def trends() -> dict:
    """Return class counts and mean behaviour per tier, with the data source."""
    settings = get_analytics_settings()
    try:
        frame, source = read_learners(settings, prefer_db=True)
    except Exception as exc:  # noqa: BLE001 - report as unavailable
        raise HTTPException(status_code=503, detail=f"Data unavailable: {exc}") from exc

    target = settings.target
    class_counts = {
        str(label): int(count) for label, count in frame[target].value_counts().items()
    }
    behaviour_by_class = (
        frame.groupby(target)[_BEHAVIOURAL].mean().round(2).to_dict(orient="index")
    )
    by_topic = (
        frame.groupby(["Topic", target])
        .size()
        .unstack(fill_value=0)
        .to_dict(orient="index")
    )

    return {
        "data_source": source,
        "total_records": int(len(frame)),
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
