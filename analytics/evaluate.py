"""Evaluation and reporting.

Accuracy, macro and weighted precision/recall/F1, confusion matrix,
one-vs-rest ROC-AUC and PR-AUC, and stratified 10-fold cross-validation. See
specification sections 4.5 and 7.
"""
from __future__ import annotations

from typing import Any

from sklearn.model_selection import StratifiedKFold, cross_val_score


def cross_validate(model: Any, features, target, folds: int = 10, seed: int = 42):
    """Return per-fold macro-F1 scores under stratified k-fold CV."""
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    return cross_val_score(model, features, target, cv=cv, scoring="f1_macro")


def classification_metrics(y_true, y_pred) -> dict[str, Any]:
    """Return the standard metric set for one fitted model."""
    raise NotImplementedError("Implemented in build-plan phase 3.")
