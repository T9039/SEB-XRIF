"""Interpretability payloads.

Native and permutation importance, cross-fold stability, and a SHAP summary
when SHAP is installed. The JSON payload is consumed by the dashboard's
importance panel. See the technical specification, section 4.7.

Examples:
    uv run python -m analytics.explain --model random_forest --folds 5
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from .config import Settings, get_settings
from .data import features_and_target, load_validated
from .models import build_pipeline


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


def cross_fold_importance(
    model_factory: Callable[[], Any],
    features,
    target,
    folds: int = 5,
    seed: int = 42,
    n_repeats: int = 5,
    n_jobs: int = 1,
) -> dict[str, Any]:
    """Permutation importance per fold, aggregated for stability analysis."""
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import StratifiedKFold

    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    per_fold: list[np.ndarray] = []
    for train_index, test_index in cv.split(features, target):
        model = model_factory()
        model.fit(features.iloc[train_index], target.iloc[train_index])
        result = permutation_importance(
            model,
            features.iloc[test_index],
            target.iloc[test_index],
            n_repeats=n_repeats,
            random_state=seed,
            scoring="f1_macro",
            n_jobs=n_jobs,
        )
        per_fold.append(np.asarray(result.importances_mean, dtype=float))

    stacked = np.vstack(per_fold)
    means = stacked.mean(axis=0)
    stds = stacked.std(axis=0)
    ranked = sorted(
        zip(features.columns, means, stds, strict=True),
        key=lambda item: item[1],
        reverse=True,
    )
    return {
        "folds": folds,
        "n_repeats": n_repeats,
        "features": [
            {"feature": name, "mean": float(mean), "std": float(std)}
            for name, mean, std in ranked
        ],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Export interpretability payloads.")
    parser.add_argument("--model", default="random_forest")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    settings: Settings = get_settings()
    frame = load_validated(settings=settings)
    features, target = features_and_target(frame, settings)

    pipeline = build_pipeline(args.model, settings.seed, settings.n_jobs)
    pipeline.fit(features, target)

    native: dict[str, Any]
    try:
        native = {"available": True, "importance": feature_importance(pipeline)}
    except AttributeError as exc:
        native = {"available": False, "reason": str(exc)}

    payload = {
        "model": args.model,
        "native": native,
        "shap": shap_payload(pipeline, features),
        "cross_fold": cross_fold_importance(
            lambda: build_pipeline(args.model, settings.seed, settings.n_jobs),
            features,
            target,
            folds=args.folds,
            seed=settings.seed,
            n_jobs=settings.n_jobs,
        ),
    }

    out = args.out or (settings.reports_dir / "explain.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
