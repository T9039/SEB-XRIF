"""SEB-XRIF prediction API.

Loads the promoted model once at startup and exposes the contract defined in
specification section 5. The model artifact and the remaining routes are wired
up in build-plan phases 7 and 8.
"""
from __future__ import annotations

from fastapi import FastAPI

from .schemas import HealthResponse

app = FastAPI(
    title="SEB-XRIF API",
    version="0.1.0",
    description=(
        "Scalable, Evidence-Based XR Integration Framework: learner "
        "performance tier prediction and analytics."
    ),
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Liveness check and model-loaded indicator."""
    return HealthResponse(status="ok", model_version="unset")
