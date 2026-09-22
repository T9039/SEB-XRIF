"""Interpretability payloads.

Native and permutation importance, and a SHAP summary when SHAP is installed.
The JSON payloads are consumed by the dashboard's importance panel. See the
technical specification, section 4.7.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def feature_names(pipeline: Any) -> list[str]:
    """Return the post-preprocessing feature names."""
    return [str(name) for name in pipeline.named_steps["pre"].get_feature_names_out()]


def feature_importance(pipeline: Any) -> dict[str, float]:
    """Return a ranked native importance mapping for a fitted model."""
    clf = pipeline.named_steps["clf"]
    names = feature_names(pipeline)
    if hasattr(clf, "feature_importances_"):
        importances = np.asarray(clf.feature_importances_, dtype=float)
    elif hasattr(clf, "coef_"):
        coef = np.asarray(clf.coef_, dtype=float)
        importances = np.abs(coef).mean(axis=0) if coef.ndim > 1 else np.abs(coef)
    else:
        raise AttributeError(
            f"{type(clf).__name__} exposes no native feature importance"
        )
    ranked = sorted(
        zip(names, importances.tolist(), strict=True),
        key=lambda kv: kv[1],
        reverse=True,
    )
    return {name: float(score) for name, score in ranked}


def permutation_importance_scores(
    pipeline: Any, features, target, n_repeats: int = 10, seed: int = 42
) -> dict[str, float]:
    """Model-agnostic permutation importance keyed by input column."""
    from sklearn.inspection import permutation_importance

    result = permutation_importance(
        pipeline,
        features,
        target,
        n_repeats=n_repeats,
        random_state=seed,
        n_jobs=-1,
        scoring="f1_macro",
    )
    ranked = sorted(
        zip(features.columns, result.importances_mean.tolist(), strict=True),
        key=lambda kv: kv[1],
        reverse=True,
    )
    return {name: float(score) for name, score in ranked}


def shap_payload(pipeline: Any, features, max_rows: int = 200) -> dict[str, Any]:
    """Return a global SHAP summary, or a graceful unavailable marker."""
    try:
        import shap
    except ImportError:
        return {"available": False, "reason": "shap is not installed"}

    try:
        pre = pipeline.named_steps["pre"]
        clf = pipeline.named_steps["clf"]
        transformed = pre.transform(features.head(max_rows))
        if hasattr(transformed, "toarray"):  # sparse one-hot output
            transformed = transformed.toarray()
        explainer = shap.TreeExplainer(clf)
        raw = explainer.shap_values(transformed)
        arr = getattr(raw, "values", raw)
        if isinstance(arr, list):  # list of per-class arrays
            arr = np.mean([np.abs(np.asarray(v, dtype=float)) for v in arr], axis=0)
        else:
            arr = np.abs(np.asarray(arr, dtype=float))
        if arr.ndim == 3:  # (n_samples, n_features, n_classes)
            arr = arr.mean(axis=2)
        mean_abs = arr.mean(axis=0).tolist()
        names = feature_names(pipeline)
        ranked = sorted(
            zip(names, mean_abs, strict=True), key=lambda kv: kv[1], reverse=True
        )
        return {
            "available": True,
            "method": "tree",
            "n_rows": int(min(len(features), max_rows)),
            "mean_abs_shap": {name: float(score) for name, score in ranked},
        }
    except Exception as exc:  # noqa: BLE001 - explanatory payload must never crash
        return {"available": False, "reason": str(exc)}
