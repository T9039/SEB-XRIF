"""Evaluation and reporting.

Accuracy, macro and weighted precision/recall/F1, confusion matrix,
one-vs-rest ROC-AUC, and stratified k-fold cross-validation. See the technical
specification, sections 4.5 and 7.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score


def classification_metrics(
    y_true: Sequence[Any],
    y_pred: Sequence[Any],
    y_proba: np.ndarray | None = None,
    labels: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Return the standard metric set for one fitted model."""
    true: np.ndarray = np.asarray(y_true)
    pred: np.ndarray = np.asarray(y_pred)
    label_list = list(labels) if labels is not None else sorted(set(true) | set(pred))

    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(true, pred)),
        "precision_macro": float(
            precision_score(true, pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(true, pred, average="macro", zero_division=0)
        ),
        "f1_macro": float(f1_score(true, pred, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(true, pred, average="weighted", zero_division=0)),
        "labels": label_list,
        "confusion_matrix": confusion_matrix(true, pred, labels=label_list).tolist(),
        "support": {label: int((true == label).sum()) for label in label_list},
    }

    if y_proba is not None:
        proba = np.asarray(y_proba)
        try:
            if proba.ndim == 2 and proba.shape[1] > 2:
                # Columns follow the estimator's sorted classes_, which matches
                # np.unique(y_true); do not pass a differently ordered label list.
                metrics["roc_auc_ovr"] = float(
                    roc_auc_score(true, proba, multi_class="ovr")
                )
            elif proba.ndim == 2 and proba.shape[1] == 2:
                metrics["roc_auc"] = float(roc_auc_score(true, proba[:, 1]))
        except ValueError:
            # ROC-AUC is undefined when a class is absent from the test split.
            pass
    return metrics


def cross_validate_model(
    model: Any,
    features,
    target,
    folds: int = 10,
    seed: int = 42,
    scoring: str = "f1_macro",
    n_jobs: int = 1,
) -> dict[str, Any]:
    """Return per-fold scores and their mean/std under stratified k-fold CV.

    Also reports a 95% confidence interval for the mean, so a small cohort is
    read with its uncertainty rather than as a point estimate.
    """
    from scipy import stats

    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    scores = cross_val_score(
        model, features, target, cv=cv, scoring=scoring, n_jobs=n_jobs
    )
    count = len(scores)
    mean = float(scores.mean())
    std = float(scores.std())
    stderr = std / np.sqrt(count) if count else 0.0
    margin = float(stats.t.ppf(0.975, df=count - 1)) * stderr if count > 1 else 0.0
    return {
        "metric": scoring,
        "folds": folds,
        "scores": [float(score) for score in scores],
        "mean": mean,
        "std": std,
        "stderr": float(stderr),
        "ci_low": float(mean - margin),
        "ci_high": float(mean + margin),
        "ci_level": 0.95,
    }
