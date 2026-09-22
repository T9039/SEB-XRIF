"""SEB-XRIF prediction API.

Loads the promoted model once at startup and exposes the contract defined in
the technical specification, section 5. The service starts even without a
trained artifact; prediction routes return HTTP 503 until one exists.

Run with:
    uv run uvicorn api.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .model_store import get_store
from .routes import importance, metrics, predict, trends
from .schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model artifact once when the service starts."""
    get_store().load()
    yield


app = FastAPI(
    title="SEB-XRIF API",
    version="0.1.0",
    description=(
        "Scalable, Evidence-Based XR Integration Framework: learner "
        "performance tier prediction and analytics."
    ),
    lifespan=lifespan,
)

app.include_router(predict.router)
app.include_router(metrics.router)
app.include_router(importance.router)
app.include_router(trends.router)


@app.get("/", tags=["system"])
def root() -> dict:
    """Service banner with documentation pointers."""
    return {
        "name": "SEB-XRIF",
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "/predict",
            "/predict/batch",
            "/metrics",
            "/importance",
            "/trends",
        ],
    }


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Liveness check and model-loaded indicator."""
    store = get_store()
    return HealthResponse(
        status="ok" if store.ready else "degraded",
        model_loaded=store.ready,
        model_version=store.version,
    )
