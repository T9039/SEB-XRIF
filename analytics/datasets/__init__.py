"""Dataset adapters for the SEB-XRIF analytics layer.

An adapter maps one raw xAPI source onto the canonical learner frame. The
pipeline asks the registry for the configured adapter instead of reading a
source directly, so a new source is a new adapter, not a branch in the core.
"""

from .base import DatasetAdapter
from .kalboard import KalboardAdapter
from .registry import get_adapter, list_datasets, register

__all__ = [
    "DatasetAdapter",
    "KalboardAdapter",
    "get_adapter",
    "list_datasets",
    "register",
]
