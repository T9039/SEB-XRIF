"""Dataset-adapter seam: registry, the Dataset contract, and the migration."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd
import pytest

from analytics.config import get_settings
from analytics.data import load_source
from analytics.datasets.base import Dataset, DatasetAdapter
from analytics.datasets.registry import get_adapter, list_datasets, register
from analytics.schema import SCHEMA


def test_registry_lists_kalboard():
    assert "kalboard" in list_datasets()


def test_unknown_dataset_raises():
    with pytest.raises(ValueError, match="Unknown dataset"):
        get_adapter("does-not-exist")


def test_kalboard_adapter_returns_a_dataset():
    dataset = get_adapter("kalboard").load(get_settings())
    assert isinstance(dataset, Dataset)
    assert dataset.source == "csv"
    assert dataset.target == "Class"
    assert dataset.class_labels == ["L", "M", "H"]
    assert dataset.features == get_settings().feature_columns
    assert dataset.supervised is True
    assert len(dataset.frame) == 480
    assert set(SCHEMA.columns) <= set(dataset.frame.columns)


def test_load_source_uses_configured_adapter():
    class Alpha(DatasetAdapter):
        name = "alpha-test"
        description = "in-test adapter"

        def load(self, settings):
            return Dataset(
                name=self.name,
                description=self.description,
                source="alpha",
                frame=pd.DataFrame({"x": [1, 2]}),
                features=["x"],
            )

    register(Alpha)
    assert "alpha-test" in list_datasets()

    settings = replace(get_settings(), dataset="alpha-test")
    frame, source = load_source(settings)
    assert source == "alpha"
    assert len(frame) == 2
