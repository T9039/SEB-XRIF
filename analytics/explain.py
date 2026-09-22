"""Interpretability payloads.

Native and permutation importance, SHAP global and per-student explanations,
and a LIME cross-check. The dashboard consumes the exported payloads. See
specification section 4.7.
"""
from __future__ import annotations

from typing import Any


def feature_importance(model: Any, feature_names: list[str]) -> dict[str, float]:
    """Return a ranked importance mapping for a fitted tree model."""
    raise NotImplementedError("Implemented in build-plan phase 5.")


def shap_payload(model: Any, features, feature_names: list[str]) -> dict[str, Any]:
    """Return global and local SHAP explanations for the dashboard."""
    raise NotImplementedError("Implemented in build-plan phase 5.")
