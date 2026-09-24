"""Derived-statistics routes powering the Chart Studio."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from analytics import aggregate

router = APIRouter(tags=["analytics"])


class QueryRequest(BaseModel):
    x: str
    y: str | None = None
    group: str | None = None
    aggregate: str = "mean"
    filters: dict[str, str] = Field(default_factory=dict)
    limit: int = 100
    sort: str = "x"


@router.get("/analytics/columns")
def columns() -> dict:
    """Column metadata (kind + categorical options) for the Studio controls."""
    return aggregate.column_metadata()


@router.post("/analytics/query")
def query(request: QueryRequest) -> dict:
    """Group the learner table and return a chart-ready table."""
    try:
        return aggregate.run_query(**request.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown column: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/analytics/correlation")
def correlation() -> dict:
    """Pearson correlation matrix of the numeric predictors."""
    return aggregate.correlation()


@router.get("/analytics/distribution")
def distribution(column: str = Query(...), bins: int = Query(10, ge=2, le=50)) -> dict:
    """Value counts or histogram for one column."""
    try:
        return aggregate.distribution(column, bins)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown column: {exc}") from exc
