"""Partial dependence for a numeric behavioural feature."""

from __future__ import annotations

from typing import Any

import joblib
import numpy as np
from sklearn.inspection import partial_dependence

from .config import Settings, get_settings
from .data import features_and_target, load_source
from .schema import BEHAVIOURAL


def compute_pdp(
    feature: str, settings: Settings | None = None, grid_points: int = 15
) -> dict[str, Any]:
    """Average partial dependence of the predicted probability on one feature."""
    settings = settings or get_settings()
    if feature not in BEHAVIOURAL:
        raise KeyError(feature)

    pipeline = joblib.load(settings.model_path)
    frame, source = load_source(settings)
    features, _target = features_and_target(frame, settings)
    # Partial dependence requires float dtypes for numeric features.
    features = features.copy()
    features[list(BEHAVIOURAL)] = features[list(BEHAVIOURAL)].astype(float)

    result = partial_dependence(
        pipeline, features, [feature], grid_resolution=grid_points, kind="average"
    )
    grid = np.asarray(result["grid_values"][0])
    average = np.asarray(result["average"])
    if average.ndim == 1:
        average = average[None, :]

    classes = [str(label) for label in pipeline.named_steps["clf"].classes_]
    rows = []
    for index, value in enumerate(grid):
        row: dict[str, Any] = {"x": round(float(value), 2)}
        for class_index, label in enumerate(classes):
            row[label] = round(float(average[class_index][index]), 4)
        rows.append(row)

    return {
        "data_source": source,
        "feature": feature,
        "classes": classes,
        "rows": rows,
    }
