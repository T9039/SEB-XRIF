"""ARETE pilots on the adapter seam, with the derived drop-off target."""

from __future__ import annotations

from pathlib import Path

import pytest

from analytics import xr
from analytics.config import get_settings
from analytics.datasets.registry import get_adapter, list_datasets

FIXTURE = Path(__file__).parent / "fixtures" / "arete" / "xAPI_PBIS.sample.csv"


def test_arete_adapters_are_registered():
    names = set(list_datasets())
    assert {
        "arete-pbis",
        "arete-english-literacy",
        "arete-stem-geometry",
        "arete-stem-geography",
        "arete-lxd",
    } <= names


def test_arete_adapter_builds_a_dropoff_dataset(monkeypatch):
    monkeypatch.setattr(xr, "pilot_path", lambda pilot, settings=None: FIXTURE)
    dataset = get_adapter("arete-pbis").load(get_settings())

    assert dataset.source == "arete-pbis"
    assert dataset.target == "dropout_risk"
    assert dataset.class_labels == ["retained", "elevated"]
    assert "verb_interaction" in dataset.features
    assert "learner" in dataset.frame.columns
    assert not dataset.frame.empty
    assert set(dataset.frame["dropout_risk"].unique()) <= {"retained", "elevated"}
    assert "derived" in dataset.description.lower()


def test_arete_adapter_rejects_an_empty_cohort(monkeypatch):
    empty = xr.parse_statements(FIXTURE).head(0)
    monkeypatch.setattr(
        xr,
        "load_pilot",
        lambda name, settings=None, path=None: (empty, xr.PILOTS["pbis"]),
    )
    with pytest.raises(ValueError, match="no usable cohort"):
        get_adapter("arete-pbis").load(get_settings())
