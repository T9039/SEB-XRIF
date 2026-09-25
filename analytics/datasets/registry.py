"""Registry of dataset adapters, keyed by the ``dataset`` config value.

Built-in adapters are code (Kalboard, the xAPI profile, the ARETE pilots).
Uploaded sources are data: a profile-conformant statements file plus a sidecar,
resolved through the generic xAPI-profile adapter.
"""

from __future__ import annotations

from .arete import (
    AreteEnglishLiteracyAdapter,
    AreteLxdAdapter,
    AretePbisAdapter,
    AreteStemGeographyAdapter,
    AreteStemGeometryAdapter,
)
from .base import DatasetAdapter
from .kalboard import KalboardAdapter
from .xapi_profile import XapiProfileAdapter

_ADAPTERS: dict[str, type[DatasetAdapter]] = {
    KalboardAdapter.name: KalboardAdapter,
    XapiProfileAdapter.name: XapiProfileAdapter,
    AretePbisAdapter.name: AretePbisAdapter,
    AreteEnglishLiteracyAdapter.name: AreteEnglishLiteracyAdapter,
    AreteStemGeometryAdapter.name: AreteStemGeometryAdapter,
    AreteStemGeographyAdapter.name: AreteStemGeographyAdapter,
    AreteLxdAdapter.name: AreteLxdAdapter,
}


def register(adapter: type[DatasetAdapter]) -> type[DatasetAdapter]:
    """Register an adapter class under its ``name`` (decorator-friendly)."""
    _ADAPTERS[adapter.name] = adapter
    return adapter


def get_adapter(name: str, settings=None) -> DatasetAdapter:
    """Return an adapter for ``name`` (built-in or uploaded) or raise."""
    if name in _ADAPTERS:
        return _ADAPTERS[name]()

    # Lazy import avoids a cycle at package import time.
    from .uploads import read_upload

    upload = read_upload(name, settings)
    return XapiProfileAdapter(
        path=upload.statements_path,
        name=upload.name,
        description=upload.description,
        target=upload.target,
        class_labels=upload.class_labels,
    )


def list_datasets() -> list[str]:
    """Return the built-in dataset names."""
    return sorted(_ADAPTERS)


def list_sources(settings=None) -> list[dict]:
    """Return every source, built-in and uploaded, in one list."""
    from .uploads import list_uploads

    sources = [
        {"name": name, "kind": "builtin", "adapter": name, "description": ""}
        for name in sorted(_ADAPTERS)
    ]
    sources += [
        {
            "name": upload.name,
            "kind": "upload",
            "adapter": XapiProfileAdapter.name,
            "description": upload.description,
        }
        for upload in list_uploads(settings)
    ]
    return sources
