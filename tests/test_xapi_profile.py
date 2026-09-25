"""The generic xAPI-profile adapter: round-trip and rejection paths."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analytics.config import get_settings
from analytics.data import load_raw
from analytics.datasets.registry import list_datasets
from analytics.datasets.xapi_profile import XapiProfileAdapter
from analytics.schema import SCHEMA
from analytics.xapi import build_statements, learner_id


def _statements_for(frame) -> list[dict]:
    statements: list[dict] = []
    for index, (_, row) in enumerate(frame.iterrows()):
        statements.extend(build_statements(row.to_dict(), learner_id(index)))
    return statements


def _write(statements: list[dict], path: Path, lines: bool = True) -> Path:
    if lines:
        path.write_text(
            "\n".join(json.dumps(statement) for statement in statements),
            encoding="utf-8",
        )
    else:
        path.write_text(json.dumps(statements), encoding="utf-8")
    return path


def test_round_trip_kalboard_to_profile(tmp_path):
    statements = _statements_for(load_raw().head(5))
    path = _write(statements, tmp_path / "statements.jsonl")

    dataset = XapiProfileAdapter(path).load(get_settings())
    assert dataset.source == "xapi-profile"
    assert dataset.target == "Class"
    assert len(dataset.frame) == 5
    assert set(SCHEMA.columns) <= set(dataset.frame.columns)


def test_reads_a_json_array_too(tmp_path):
    statements = _statements_for(load_raw().head(3))
    path = _write(statements, tmp_path / "statements.json", lines=False)
    dataset = XapiProfileAdapter(path).load(get_settings())
    assert len(dataset.frame) == 3


def test_adapter_is_registered():
    assert "xapi-profile" in list_datasets()


def test_non_conformant_file_is_rejected(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps({"verb": {"id": "x"}}), encoding="utf-8")
    with pytest.raises(ValueError):
        XapiProfileAdapter(path).load(get_settings())


def test_missing_target_is_rejected(tmp_path):
    completed = "http://adlnet.gov/expapi/verbs/completed"
    statements = [
        statement
        for statement in _statements_for(load_raw().head(3))
        if statement["verb"]["id"] != completed
    ]
    path = _write(statements, tmp_path / "no_target.jsonl")
    with pytest.raises(ValueError, match="target"):
        XapiProfileAdapter(path).load(get_settings())
