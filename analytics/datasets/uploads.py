"""Uploaded sources: a data file plus a sidecar describing it.

Two kinds:

- **statements** — a profile-conformant xAPI statements file (``<name>.jsonl``),
  resolved through the generic xAPI-profile adapter.
- **table** — a plain CSV adapted to the Dataset contract by a column mapping
  (``<name>.csv``), resolved through the table adapter.

Both are data, never code. The sidecar (``<name>.json``) declares the kind, the
target, the class labels, and (for tables) the feature columns.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..config import Settings, get_settings


@dataclass(frozen=True)
class UploadSource:
    """A source registered from an uploaded file."""

    name: str
    kind: str
    description: str
    path: Path
    target: str | None
    class_labels: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    categorical: list[str] = field(default_factory=list)
    numeric: list[str] = field(default_factory=list)
    delimiter: str | None = None


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
    kind = str(meta.get("kind", "statements"))
    default = f"{name}.jsonl" if kind == "statements" else f"{name}.csv"
    filename = str(meta.get("data") or meta.get("statements") or default)
    data_path = settings.uploads_dir / filename
    if not data_path.exists():
        raise ValueError(f"Upload '{name}' is missing its data file {data_path}.")

    return UploadSource(
        name=name,
        kind=kind,
        description=str(meta.get("description", "")),
        path=data_path,
        target=meta.get("target"),
        class_labels=list(meta.get("class_labels", [])),
        features=list(meta.get("features", [])),
        categorical=list(meta.get("categorical", [])),
        numeric=list(meta.get("numeric", [])),
        delimiter=meta.get("delimiter"),
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


def _write_sidecar(name: str, meta: dict, settings: Settings) -> None:
    sidecar_path(name, settings).write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )


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
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    data_file = settings.uploads_dir / f"{name}.jsonl"
    data_file.write_text(statements, encoding="utf-8")
    _write_sidecar(
        name,
        {
            "name": name,
            "kind": "statements",
            "description": description,
            "target": target,
            "class_labels": class_labels or [],
            "data": data_file.name,
        },
        settings,
    )
    return read_upload(name, settings)


def write_table_upload(
    name: str,
    data: bytes,
    *,
    target: str,
    features: list[str],
    categorical: list[str] | None = None,
    numeric: list[str] | None = None,
    class_labels: list[str] | None = None,
    delimiter: str | None = None,
    description: str = "",
    settings: Settings | None = None,
) -> UploadSource:
    """Persist an adapted CSV table and sidecar, returning the source."""
    settings = settings or get_settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    data_file = settings.uploads_dir / f"{name}.csv"
    data_file.write_bytes(data)
    _write_sidecar(
        name,
        {
            "name": name,
            "kind": "table",
            "description": description,
            "target": target,
            "class_labels": class_labels or [],
            "features": features,
            "categorical": categorical or [],
            "numeric": numeric or features,
            "delimiter": delimiter,
            "data": data_file.name,
        },
        settings,
    )
    return read_upload(name, settings)
