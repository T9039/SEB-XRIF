"""SEB-XRIF prediction API.

Loads the promoted model once at startup and exposes the contract defined in
the technical specification, section 5. The service starts even without a
trained model; prediction routes return HTTP 503 until one exists.

Run with:
    uv run uvicorn api.main:app --reload
"""

from __future__ import annotations

import platform
import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from .logging import configure_logging, get_logger
from .model_store import get_store
from .routes import (
    advanced,
    analytics,
    charts,
    datasets,
    diagnostics,
    evaluation,
    importance,
    learners,
    metrics,
    predict,
    results,
    trends,
    xr,
)
from .schemas import HealthResponse

configure_logging()
logger = get_logger("api")


def _error_response(status_code: int, message: str) -> JSONResponse:
    request_id = structlog.contextvars.get_contextvars().get("request_id")
    return JSONResponse(
        status_code=status_code,
        content={"error": {"message": str(message), "request_id": request_id}},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model artifact once when the service starts."""
    store = get_store().load()
    logger.info("startup", model_loaded=store.ready, model_version=store.version)
    yield
    logger.info("shutdown")


app = FastAPI(
    title="SEB-XRIF API",
    version="0.1.0",
    description=(
        "Scalable, Evidence-Based XR Integration Framework: learner "
        "performance tier prediction and analytics."
    ),
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    """Attach a request id and emit a structured access log line."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id, method=request.method, path=request.url.path
    )
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed")
        raise
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info("request", status=response.status_code, duration_ms=duration_ms)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return _error_response(exc.status_code, exc.detail)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error")
    return _error_response(500, "Internal Server Error")


app.include_router(predict.router)
app.include_router(metrics.router)
app.include_router(importance.router)
app.include_router(trends.router)
app.include_router(learners.router)
app.include_router(results.router)
app.include_router(analytics.router)
app.include_router(advanced.router)
app.include_router(charts.router)
app.include_router(diagnostics.router)
app.include_router(xr.router)
app.include_router(evaluation.router)
app.include_router(datasets.router)


@app.get("/", tags=["system"])
def root() -> dict:
    """Service banner with documentation pointers."""
    return {
        "name": "SEB-XRIF",
        "docs": "/docs",
        "health": "/health",
        "version": "/version",
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


@app.get("/version", tags=["system"])
def version() -> dict:
    """Return application, model, and runtime versions."""
    store = get_store()
    return {
        "app_version": app.version,
        "model_version": store.version,
        "model_loaded": store.ready,
        "python": platform.python_version(),
        "git_commit": store.metadata.get("git_commit", "unknown"),
    }
