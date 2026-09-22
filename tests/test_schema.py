"""Tests for the dataset schema and validation."""

from __future__ import annotations

import pandera.errors as pa_errors
import pytest

from analytics.data import load_raw, validate
from analytics.schema import SCHEMA


def test_raw_dataset_loads():
    df = load_raw()
    assert len(df) == 480
    assert "Class" in df.columns


def test_validation_passes_on_clean_data():
    df = validate(load_raw())
    assert set(df["Class"].unique()) <= {"L", "M", "H"}


def test_validation_rejects_bad_target():
    df = load_raw()
    df.loc[0, "Class"] = "Z"
    with pytest.raises(pa_errors.SchemaErrors):
        SCHEMA.validate(df, lazy=True)


def test_validation_rejects_negative_behaviour():
    df = load_raw()
    df.loc[0, "raisedhands"] = -1
    with pytest.raises(pa_errors.SchemaErrors):
        SCHEMA.validate(df, lazy=True)
