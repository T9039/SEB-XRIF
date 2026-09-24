"""Model-results routes: serve the matrices produced by the reports pipeline."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException

from analytics.config import get_settings

router = APIRouter(tags=["analytics"])


def _load(name: str) -> Any:
    path = get_settings().reports_dir / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/results")
def results() -> dict:
    """Return the model comparison matrix plus tuning and explanation payloads."""
    matrix = _load("results.json")
    if matrix is None:
        raise HTTPException(
            status_code=503,
            detail="No results yet. Run: make matrix",
        )
    return {
        "results": matrix,
        "tuning": _load("tuning.json"),
        "explain": _load("explain.json"),
        "evaluation": _load("evaluation.json"),
    }
