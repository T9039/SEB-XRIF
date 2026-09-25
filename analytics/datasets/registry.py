"""Registry of dataset adapters, keyed by the ``dataset`` config value."""

from __future__ import annotations

from .base import DatasetAdapter
from .kalboard import KalboardAdapter

_ADAPTERS: dict[str, type[DatasetAdapter]] = {
    KalboardAdapter.name: KalboardAdapter,
}


def register(adapter: type[DatasetAdapter]) -> type[DatasetAdapter]:
    """Register an adapter class under its ``name`` (decorator-friendly)."""
    _ADAPTERS[adapter.name] = adapter
    return adapter


def get_adapter(name: str) -> DatasetAdapter:
    """Return an adapter instance for ``name`` or raise ``ValueError``."""
    try:
        return _ADAPTERS[name]()
    except KeyError:
        known = ", ".join(sorted(_ADAPTERS))
        raise ValueError(f"Unknown dataset '{name}'. Known datasets: {known}") from None


def list_datasets() -> list[str]:
    """Return the registered dataset names."""
    return sorted(_ADAPTERS)
