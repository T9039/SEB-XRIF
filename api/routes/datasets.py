"""Dataset source management: check, list, upload/adapt, delete, and train.

An upload is checked first. A profile-conformant statements file is accepted as
is; a plain table is adapted to the Dataset contract through a column mapping
(the target column and the feature columns), which never fabricates values — if
a required column is absent the adaptation is refused. Everything is data; no
code is executed.
"""

from __future__ import annotations

import io
import json
import re
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from analytics.config import get_settings
from analytics.datasets.registry import get_adapter, list_datasets, list_sources
from analytics.datasets.uploads import (
    read_upload,
    sidecar_path,
    write_table_upload,
    write_upload,
)
from analytics.train import train_source
from analytics.xapi import inspect_statements, statements_from_text

router = APIRouter(tags=["datasets"])

MAX_BYTES = 20_000_000
_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")
_STATEMENT_SUFFIXES = (".json", ".jsonl")
_TABLE_SUFFIXES = (".csv", ".tsv")
_TARGET_GUESSES = ("Class", "class", "target", "label", "final_result", "outcome")


def _trained(source: str, settings) -> bool:
    return settings.artifacts_for(source)[0].exists()


def _remove(name: str, settings) -> None:
    try:
        read_upload(name, settings).path.unlink(missing_ok=True)
    except ValueError:
        for suffix in (".jsonl", ".csv"):
            (settings.uploads_dir / f"{name}{suffix}").unlink(missing_ok=True)
    sidecar_path(name, settings).unlink(missing_ok=True)


def _read_table(data: bytes, filename: str) -> pd.DataFrame:
    sep = "\t" if filename.endswith(".tsv") else ","
    return pd.read_csv(io.BytesIO(data), sep=sep)


def _table_report(data: bytes, filename: str) -> dict:
    try:
        frame = _read_table(data, filename)
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
        return {
            "kind": "table",
            "conformant": False,
            "adaptable": False,
            "reason": str(exc),
        }

    columns = [str(column) for column in frame.columns]
    if len(columns) == 1 and (";" in columns[0] or "\t" in columns[0]):
        return {
            "kind": "table",
            "conformant": False,
            "adaptable": False,
            "columns": columns,
            "reason": (
                "Parsed as a single column; the delimiter may be ';' or tab. "
                "Re-export as comma-separated CSV."
            ),
        }
    target = next((name for name in _TARGET_GUESSES if name in columns), None)
    actor = next(
        (
            name
            for name in ("id_student", "student_id", "id", "learner")
            if name in columns
        ),
        None,
    )
    features = [column for column in columns if column not in {target, actor}]
    categorical = [
        column
        for column in features
        if not pd.api.types.is_numeric_dtype(frame[column])
    ]
    numeric = [column for column in features if column not in categorical]

    missing = [] if target else ["no target column found; set one in the mapping"]
    return {
        "kind": "table",
        "conformant": False,
        "adaptable": bool(target) and bool(features),
        "missing": missing,
        "columns": columns,
        "suggested_mapping": {
            "target": target,
            "actor": actor,
            "features": features,
            "categorical": categorical,
            "numeric": numeric,
        },
    }


def _check_upload(data: bytes, filename: str) -> dict:
    if filename.endswith(_TABLE_SUFFIXES):
        return _table_report(data, filename)
    text = data.decode("utf-8")
    report = inspect_statements(statements_from_text(text))
    report["kind"] = "statements"
    report["adaptable"] = bool(report["conformant"])
    if not report["conformant"]:
        report["reason"] = (
            "This statements file does not follow the framework profile. Adapt it "
            "into the profile, or upload a table with a column mapping, or write an "
            "adapter: " + "; ".join(report["missing"])
        )
    return report


@router.post("/datasets/check")
async def check(file: Annotated[UploadFile, File()]) -> dict:
    """Inspect an upload and report conformance / adaptability without storing it."""
    filename = file.filename or ""
    if not filename.endswith((*_STATEMENT_SUFFIXES, *_TABLE_SUFFIXES)):
        raise HTTPException(
            status_code=400, detail="Only .json/.jsonl/.csv/.tsv files."
        )
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty upload.")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Upload exceeds the size limit.")
    try:
        return _check_upload(data, filename)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
    target: Annotated[str, Form()] = "",
    class_labels: Annotated[str, Form()] = "",
    mapping: Annotated[str, Form()] = "",
    train: Annotated[bool, Form()] = False,
    mode: Annotated[str, Form()] = "best",
    model: Annotated[str, Form()] = "",
) -> dict:
    """Check, then store an upload — adapting a table with a mapping if needed."""
    if not _NAME.match(name):
        raise HTTPException(
            status_code=400,
            detail="Invalid source name; use lowercase letters, digits and hyphens.",
        )
    filename = file.filename or ""
    if not filename.endswith((*_STATEMENT_SUFFIXES, *_TABLE_SUFFIXES)):
        raise HTTPException(
            status_code=400, detail="Only .json/.jsonl/.csv/.tsv files."
        )

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Empty upload.")
    if len(payload) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Upload exceeds the size limit.")

    settings = get_settings()
    if sidecar_path(name, settings).exists() or name in list_datasets():
        raise HTTPException(status_code=409, detail=f"Source '{name}' already exists.")

    try:
        if filename.endswith(_TABLE_SUFFIXES):
            kind = "table"
            report = _upload_table(
                name, payload, filename, target, mapping, description, settings
            )
        else:
            kind = "statements"
            report = _upload_statements(
                name, payload, target, class_labels, description, settings
            )
    except HTTPException:
        _remove(name, settings)
        raise
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        _remove(name, settings)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = {"name": name, "kind": kind, **report}
    if train:
        try:
            promoted = train_source(
                name,
                settings,
                models=[model] if model else None,
                matrix=mode != "single",
                no_mlflow=True,
            )
            result["trained"] = True
            result["model"] = promoted["model"]
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


def _upload_statements(
    name, payload, target, class_labels, description, settings
) -> dict:
    text = payload.decode("utf-8")
    report = inspect_statements(statements_from_text(text))
    if not report["conformant"]:
        raise HTTPException(
            status_code=422,
            detail={
                "message": (
                    "Not profile-conformant; adapt it or upload a table with a mapping."
                ),
                "missing": report["missing"],
            },
        )
    labels = [value.strip() for value in class_labels.split(",") if value.strip()]
    write_upload(
        name,
        text,
        description=description,
        target=target or None,
        class_labels=labels,
        settings=settings,
    )
    dataset = get_adapter(name, settings).load(settings)
    return {"target": dataset.target, "learners": int(len(dataset.frame))}


def _upload_table(
    name, payload, filename, target, mapping, description, settings
) -> dict:
    frame = _read_table(payload, filename)
    columns = [str(column) for column in frame.columns]
    spec = json.loads(mapping) if mapping else {}

    target_column = (
        target
        or spec.get("target")
        or next((guess for guess in _TARGET_GUESSES if guess in columns), None)
    )
    if not target_column or target_column not in columns:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "No usable target column; set 'target' (form or mapping).",
                "columns": columns,
            },
        )

    actor = spec.get("actor")
    features = spec.get("features") or [
        column for column in columns if column not in {target_column, actor}
    ]
    missing = [column for column in features if column not in columns]
    if missing or not features:
        raise HTTPException(
            status_code=422,
            detail={"message": "Mapping names unknown columns.", "missing": missing},
        )

    categorical = spec.get("categorical") or [
        column
        for column in features
        if not pd.api.types.is_numeric_dtype(frame[column])
    ]
    numeric = spec.get("numeric") or [
        column for column in features if column not in categorical
    ]
    labels = [
        value.strip()
        for value in str(spec.get("class_labels", "")).split(",")
        if value.strip()
    ]

    write_table_upload(
        name,
        payload,
        target=target_column,
        features=features,
        categorical=categorical,
        numeric=numeric,
        class_labels=labels,
        description=description,
        settings=settings,
    )
    dataset = get_adapter(name, settings).load(settings)
    return {
        "target": dataset.target,
        "learners": int(len(dataset.frame)),
        "features": features,
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
