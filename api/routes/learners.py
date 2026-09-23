"""Learner data routes: a paged table and the categorical option sets."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from analytics.config import get_settings as get_analytics_settings
from analytics.data import read_learners
from analytics.schema import CATEGORICAL

router = APIRouter(tags=["data"])


def _frame():
    settings = get_analytics_settings()
    try:
        return read_learners(settings, prefer_db=True)
    except Exception as exc:  # noqa: BLE001 - report as unavailable
        raise HTTPException(status_code=503, detail=f"Data unavailable: {exc}") from exc


@router.get("/learners")
def learners(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    topic: str | None = None,
    tier: str | None = Query(None, alias="class"),
) -> dict:
    """Return a filtered, paged slice of the learner table."""
    frame, source = _frame()

    if topic:
        frame = frame[frame["Topic"] == topic]
    if tier:
        frame = frame[frame["Class"] == tier]

    total = int(len(frame))
    page = frame.iloc[offset : offset + limit]
    return {
        "data_source": source,
        "total": total,
        "limit": limit,
        "offset": offset,
        "rows": page.to_dict(orient="records"),
    }


@router.get("/options")
def options() -> dict:
    """Return the sorted unique values for each categorical predictor."""
    frame, source = _frame()
    return {
        "data_source": source,
        "options": {
            column: sorted(str(value) for value in frame[column].dropna().unique())
            for column in CATEGORICAL
        },
    }
