"""Model diagnostics computed server-side from the promoted pipeline.

Produces chart-ready curves for a researcher dashboard: one-vs-rest ROC and
precision-recall curves, a calibration (reliability) curve, Brier scores, and a
learning curve. Out-of-fold predictions are used so the curves reflect
generalisation rather than the training fit.
"""

from __future__ import annotations

from typing import Any

import joblib
import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, learning_curve

from .config import Settings, get_settings
from .data import features_and_target, load_source

GRID = np.linspace(0.0, 1.0, 21)


def _interp(grid: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> list[float]:
    """Interpolate ys at grid points, sorted by xs and clipped to the range."""
    order = np.argsort(xs)
    xs_sorted = xs[order]
    ys_sorted = ys[order]
    values = np.interp(grid, xs_sorted, ys_sorted)
    return [round(float(value), 4) for value in values]


def compute_diagnostics(
    settings: Settings | None = None, folds: int = 5
) -> dict[str, Any]:
    """Compute ROC/PR/calibration/learning curves for the promoted model."""
    settings = settings or get_settings()
    pipeline = joblib.load(settings.model_path)

    frame, source = load_source(settings)
    features, target = features_and_target(frame, settings)
    classes = [str(label) for label in pipeline.named_steps["clf"].classes_]

    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=settings.seed)
    probabilities = cross_val_predict(
        pipeline, features, target, cv=cv, method="predict_proba"
    )
    indicator = np.asarray(target)

    roc_rows: list[dict[str, Any]] = [{"x": round(float(x), 4)} for x in GRID]
    pr_rows: list[dict[str, Any]] = [{"x": round(float(x), 4)} for x in GRID]
    calibration_rows: list[dict[str, Any]] = [{"x": round(float(x), 4)} for x in GRID]
    auc: dict[str, float] = {}
    average_precision: dict[str, float] = {}
    brier: dict[str, float] = {}

    for index, label in enumerate(classes):
        binary = (indicator == label).astype(int)
        scores = probabilities[:, index]

        fpr, tpr, _ = roc_curve(binary, scores)
        roc_rows_tpr = np.interp(GRID, fpr, tpr)
        auc[label] = round(float(roc_auc_score(binary, scores)), 4)
        for row, value in zip(roc_rows, roc_rows_tpr, strict=True):
            row[label] = round(float(value), 4)

        precision, recall, _ = precision_recall_curve(binary, scores)
        precision_values = _interp(GRID, recall, precision)
        average_precision[label] = round(
            float(average_precision_score(binary, scores)), 4
        )
        for row, value in zip(pr_rows, precision_values, strict=True):
            row[label] = value

        # Reliability curve: bin the predicted probability (x) against the
        # observed frequency (y), interpolated onto a shared grid.
        bins = np.linspace(0.0, 1.0, 11)
        bin_index = np.clip(np.digitize(scores, bins) - 1, 0, len(bins) - 2)
        prob_pred, prob_true = [], []
        for bin_id in range(len(bins) - 1):
            mask = bin_index == bin_id
            if mask.any():
                prob_pred.append(float(scores[mask].mean()))
                prob_true.append(float(binary[mask].mean()))
        calibration_values = _interp(GRID, np.asarray(prob_pred), np.asarray(prob_true))
        brier[label] = round(float(brier_score_loss(binary, scores)), 4)
        for row, value in zip(calibration_rows, calibration_values, strict=True):
            row[label] = value

    train_sizes, train_scores, test_scores = learning_curve(
        pipeline,
        features,
        target,
        cv=cv,
        scoring="f1_macro",
        train_sizes=np.linspace(0.2, 1.0, 5),
        random_state=settings.seed,
        n_jobs=1,
    )
    learning_rows = [
        {
            "x": int(size),
            "train": round(float(train_scores[i].mean()), 4),
            "test": round(float(test_scores[i].mean()), 4),
        }
        for i, size in enumerate(train_sizes)
    ]

    macro_auc = round(float(np.mean(list(auc.values()))), 4)
    return {
        "data_source": source,
        "folds": folds,
        "classes": classes,
        "macro_auc": macro_auc,
        "auc": auc,
        "average_precision": average_precision,
        "brier": brier,
        "roc": roc_rows,
        "pr": pr_rows,
        "calibration": calibration_rows,
        "learning": learning_rows,
    }
