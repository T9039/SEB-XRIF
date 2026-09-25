"""Uploaded sources and the unified source registry."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from analytics.config import get_settings
from analytics.data import load_raw
from analytics.datasets.registry import get_adapter, list_sources
from analytics.datasets.uploads import write_upload
from analytics.xapi import build_statements, learner_id


def _settings(tmp_path):
    return replace(get_settings(), repo_root=tmp_path)


def _statements_text(n: int = 4) -> str:
    statements: list[dict] = []
    for index, (_, row) in enumerate(load_raw().head(n).iterrows()):
        statements.extend(build_statements(row.to_dict(), learner_id(index)))
    return "\n".join(json.dumps(statement) for statement in statements)


def test_builtin_sources_are_listed():
    names = {source["name"] for source in list_sources()}
    assert {"kalboard", "xapi-profile", "arete-pbis"} <= names


def test_write_and_load_an_upload(tmp_path):
    settings = _settings(tmp_path)
    write_upload(
        "my-pilot",
        _statements_text(4),
        description="demo source",
        target="Class",
        class_labels=["L", "M", "H"],
        settings=settings,
    )

    sources = {source["name"]: source for source in list_sources(settings)}
    assert sources["my-pilot"]["kind"] == "upload"

    dataset = get_adapter("my-pilot", settings).load(settings)
    assert dataset.source == "my-pilot"
    assert dataset.target == "Class"
    assert dataset.class_labels == ["L", "M", "H"]
    assert len(dataset.frame) == 4


def test_unknown_source_raises():
    with pytest.raises(ValueError, match="Unknown source"):
        get_adapter("does-not-exist")


def test_incomplete_upload_is_skipped(tmp_path):
    settings = _settings(tmp_path)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    (settings.uploads_dir / "broken.json").write_text(
        json.dumps({"description": "missing statements"}), encoding="utf-8"
    )
    assert all(source["name"] != "broken" for source in list_sources(settings))
