"""Longitudinal evaluation summary route."""

from __future__ import annotations

from fastapi import APIRouter, Query

from analytics.evaluation import evaluation_summary

router = APIRouter(tags=["evaluation"])


@router.get("/evaluation")
def evaluation(
    source: str | None = Query(
        None, description="Provenance tag to filter by (e.g. pilot, example)."
    ),
) -> dict:
    """Return the usability and learning/retention summary from the store."""
    return evaluation_summary(source=source)
