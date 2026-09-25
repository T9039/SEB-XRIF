"""Uploaded sources: a profile-conformant statements file plus a sidecar.

An upload is two files in the uploads directory: ``<name>.jsonl`` (the xAPI
statements) and ``<name>.json`` (a sidecar declaring the target, class labels and
description). Both are data, never code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..config import Settings, get_settings


@dataclass(frozen=True)
class UploadSource:
    """A source registered from an uploaded statements file."""

    name: str
    description: str
    statements_path: Path
    target: str | None
    class_labels: list[str]


def sidecar_path(name: str, settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    return settings.uploads_dir / f"{name}.json"


def read_upload(name: str, settings: Settings | None = None) -> UploadSource:
    """Return the upload registered under ``name`` or raise ``ValueError``."""
    settings = settings or get_settings()
    sidecar = sidecar_path(name, settings)
    if not sidecar.exists():
        known = ", ".join(sorted(u.name for u in list_uploads(settings)))
        raise ValueError(f"Unknown source '{name}'. Known sources: {known or 'none'}.")

    meta = json.loads(sidecar.read_text(encoding="utf-8"))
    filename = str(meta.get("statements") or f"{name}.jsonl")
    statements = settings.uploads_dir / filename
    if not statements.exists():
        raise ValueError(
            f"Upload '{name}' is missing its statements file {statements}."
        )
    return UploadSource(
        name=name,
        description=str(meta.get("description", "")),
        statements_path=statements,
        target=meta.get("target"),
        class_labels=list(meta.get("class_labels", [])),
    )


def list_uploads(settings: Settings | None = None) -> list[UploadSource]:
    """Return every registered upload, ignoring incomplete ones."""
    settings = settings or get_settings()
    directory = settings.uploads_dir
    if not directory.exists():
        return []
    uploads: list[UploadSource] = []
    for sidecar in sorted(directory.glob("*.json")):
        try:
            uploads.append(read_upload(sidecar.stem, settings))
        except ValueError:
            continue
    return uploads


def write_upload(
    name: str,
    statements: str,
    *,
    description: str = "",
    target: str | None = None,
    class_labels: list[str] | None = None,
    settings: Settings | None = None,
) -> UploadSource:
    """Persist a statements file and sidecar, returning the registered source."""
    settings = settings or get_settings()
    directory = settings.uploads_dir
    directory.mkdir(parents=True, exist_ok=True)

    statements_file = directory / f"{name}.jsonl"
    statements_file.write_text(statements, encoding="utf-8")
    meta = {
        "name": name,
        "description": description,
        "target": target,
        "class_labels": class_labels or [],
        "statements": statements_file.name,
    }
    sidecar_path(name, settings).write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    return read_upload(name, settings)
