"""XR (ARETE) routes: pilot availability and engagement trends.

These routes read the downloaded ARETE xAPI pilots. If a pilot has not been
downloaded the trends route returns 503 with the fetch instruction rather than
an empty chart.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from analytics import xr

router = APIRouter(tags=["xr"])


@router.get("/xr/pilots")
def xr_pilots() -> dict:
    """Return the known ARETE pilots and whether each is downloaded."""
    return {
        "licence": xr.ARETE_LICENCE,
        "doi": xr.ARETE_DOI,
        "pilots": xr.available_pilots(),
    }


@router.get("/xr/trends")
def xr_trends(
    pilot: str = Query("pbis", description="ARETE pilot name."),
    freq: str = Query("W", description="Timeline bucket: D, W or M."),
) -> dict:
    """Return descriptive engagement over time for one XR pilot."""
    try:
        statements, meta = xr.load_pilot(pilot)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        trends = xr.engagement_trends(statements, freq=freq)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "pilot": meta.name,
        "description": meta.description,
        "licence": xr.ARETE_LICENCE,
        "doi": xr.ARETE_DOI,
        **trends,
    }
