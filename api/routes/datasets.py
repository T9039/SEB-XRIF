"""Dataset source management: list, upload, delete, and train.

Uploads are data only: a profile-conformant statements file plus a sidecar. The
file is size- and type-limited and validated against the framework profile
before it is registered; nothing is executed.
"""

from __future__ import annotations

import re
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from analytics.config import get_settings
from analytics.datasets.registry import get_adapter, list_datasets, list_sources
from analytics.datasets.uploads import read_upload, sidecar_path, write_upload
from analytics.train import train_source

router = APIRouter(tags=["datasets"])

MAX_BYTES = 20_000_000
_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")


def _trained(source: str, settings) -> bool:
    return settings.artifacts_for(source)[0].exists()


def _remove(name: str, settings) -> None:
    try:
        read_upload(name, settings).statements_path.unlink(missing_ok=True)
    except ValueError:
        (settings.uploads_dir / f"{name}.jsonl").unlink(missing_ok=True)
    sidecar_path(name, settings).unlink(missing_ok=True)


@router.get("/datasets")
def datasets() -> dict:
    """List every source, built-in and uploaded, with its trained status."""
    settings = get_settings()
    sources = [
        {**source, "trained": _trained(source["name"], settings)}
        for source in list_sources(settings)
    ]
    return {"sources": sources}


@router.post("/datasets")
async def upload(
    file: Annotated[UploadFile, File()],
    name: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    target: Annotated[str, Form()] = "Class",
    class_labels: Annotated[str, Form()] = "",
) -> dict:
    """Validate and register an uploaded profile-conformant statements file."""
    if not _NAME.match(name):
        raise HTTPException(
            status_code=400,
            detail="Invalid source name; use lowercase letters, digits and hyphens.",
        )
    filename = file.filename or ""
    if not filename.endswith((".json", ".jsonl")):
        raise HTTPException(status_code=400, detail="Only .json or .jsonl files.")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Empty upload.")
    if len(payload) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Upload exceeds the size limit.")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400, detail="Upload must be UTF-8 text."
        ) from exc

    settings = get_settings()
    if sidecar_path(name, settings).exists() or name in list_datasets():
        raise HTTPException(status_code=409, detail=f"Source '{name}' already exists.")

    labels = [value.strip() for value in class_labels.split(",") if value.strip()]
    write_upload(
        name,
        text,
        description=description,
        target=target or None,
        class_labels=labels,
        settings=settings,
    )
    try:
        dataset = get_adapter(name, settings).load(settings)
    except ValueError as exc:
        _remove(name, settings)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "name": name,
        "description": description,
        "target": dataset.target,
        "learners": int(len(dataset.frame)),
        "features": dataset.features,
    }


@router.delete("/datasets/{name}")
def delete(name: str) -> dict:
    """Delete an uploaded source (built-ins cannot be deleted)."""
    settings = get_settings()
    if name in list_datasets():
        raise HTTPException(
            status_code=400, detail="Built-in sources cannot be deleted."
        )
    if not sidecar_path(name, settings).exists():
        raise HTTPException(status_code=404, detail=f"No uploaded source '{name}'.")
    _remove(name, settings)
    return {"deleted": name}


@router.post("/datasets/{name}/train")
def train(name: str, mode: str = "best", model: str | None = None) -> dict:
    """Train and promote a model for a source (best-of-matrix or one model)."""
    settings = get_settings()
    if name not in list_datasets() and not sidecar_path(name, settings).exists():
        raise HTTPException(status_code=404, detail=f"No source '{name}'.")

    matrix = mode == "matrix"
    try:
        promoted = train_source(
            name,
            settings,
            models=[model] if model else None,
            matrix=matrix,
            no_mlflow=True,
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "source": name,
        "model": promoted["model"],
        "metrics": promoted["metrics"],
    }
