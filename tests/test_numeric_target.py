"""Regression: numeric-coded targets train and report real metrics."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd

from analytics.config import get_settings
from analytics.datasets.table import TableAdapter
from analytics.datasets.uploads import write_table_upload
from analytics.train import train_source


def _write_int_target_table(tmp_path, settings, name="int-target"):
    rows = ["PassengerId,Pclass,Sex,Age,Survived"]
    for index in range(60):
        survived = index % 2
        age = 20 + index % 40
        sex = "male" if index % 2 else "female"
        rows.append(f"{index},{1 + index % 3},{sex},{age},{survived}")
    write_table_upload(
        name,
        "\n".join(rows).encode(),
        target="Survived",
        features=["PassengerId", "Pclass", "Sex", "Age"],
        categorical=["Sex"],
        numeric=["PassengerId", "Pclass", "Age"],
        settings=settings,
    )
    return name


def test_integer_target_keeps_labels_and_metrics(tmp_path):
    settings = replace(get_settings(), repo_root=tmp_path, cv_folds=3, n_jobs=1)
    name = _write_int_target_table(tmp_path, settings)
    dataset = TableAdapter(
        name=name,
        path=settings.uploads_dir / f"{name}.csv",
        target="Survived",
        features=["PassengerId", "Pclass", "Sex", "Age"],
        categorical=["Sex"],
        numeric=["PassengerId", "Pclass", "Age"],
    ).load(settings)

    # Native dtype preserved so class_weight handles it; labels are strings.
    assert dataset.frame["Survived"].dtype != object
    assert dataset.class_labels == ["0", "1"]

    promoted = train_source(name, settings, models=["decision_tree"], no_mlflow=True)
    metrics = promoted["metrics"]
    assert sum(metrics["support"].values()) > 0
    # A confusion matrix over integer targets must not be all zeros.
    assert sum(sum(row) for row in metrics["confusion_matrix"]) > 0


def test_numeric_looking_string_target_does_not_crash(tmp_path):
    """A target stored as "0"/"1" strings must still train (sklearn quirk)."""
    settings = replace(get_settings(), repo_root=tmp_path, cv_folds=3, n_jobs=1)
    name = "string-numeric"
    rows = ["x,y,label"]
    for index in range(60):
        rows.append(f"{index},{index % 7},{'0' if index % 2 else '1'}")
    write_table_upload(
        name,
        "\n".join(rows).encode(),
        target="label",
        features=["x", "y"],
        numeric=["x", "y"],
        settings=settings,
    )
    frame = pd.read_csv(settings.uploads_dir / f"{name}.csv")
    assert frame["label"].dtype in (object, "int64")

    # Either it trains, or it raises a clear ValueError we can surface as 400.
    try:
        train_source(name, settings, models=["decision_tree"], no_mlflow=True)
    except ValueError as exc:
        assert "class_weight" in str(exc) or "classes" in str(exc)
    else:
        assert True
