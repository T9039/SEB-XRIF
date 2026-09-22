"""Hyperparameter tuning with Optuna.

Each supported model has a search space expressed as bare parameter names
relative to the pipeline's ``clf`` step. XGBoost keys are prefixed with
``estimator__`` because it is wrapped in ``LabelEncodedClassifier``.

Examples:
    uv run python -m analytics.tune --models random_forest xgboost --trials 30
    uv run python -m analytics.tune --list
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from sklearn.pipeline import Pipeline

from .config import Settings, get_settings
from .data import features_and_target, load_validated
from .evaluate import cross_validate_model
from .models import build_pipeline

SearchSpace = Callable[[Any], dict[str, Any]]


def _space_random_forest(trial: Any) -> dict[str, Any]:
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 600, step=100),
        "max_depth": trial.suggest_int("max_depth", 2, 30),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
        "max_features": trial.suggest_categorical(
            "max_features", ["sqrt", "log2", None]
        ),
    }


def _space_extra_trees(trial: Any) -> dict[str, Any]:
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 600, step=100),
        "max_depth": trial.suggest_int("max_depth", 2, 30),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
        "max_features": trial.suggest_categorical(
            "max_features", ["sqrt", "log2", None]
        ),
    }


def _space_gradient_boosting(trial: Any) -> dict[str, Any]:
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
        "max_depth": trial.suggest_int("max_depth", 2, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
    }


def _space_hist_gradient_boosting(trial: Any) -> dict[str, Any]:
    return {
        "max_iter": trial.suggest_int("max_iter", 100, 500, step=50),
        "max_depth": trial.suggest_int("max_depth", 2, 12),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "l2_regularization": trial.suggest_float(
            "l2_regularization", 1e-4, 1.0, log=True
        ),
    }


def _space_xgboost(trial: Any) -> dict[str, Any]:
    return {
        "estimator__n_estimators": trial.suggest_int(
            "n_estimators", 100, 600, step=100
        ),
        "estimator__max_depth": trial.suggest_int("max_depth", 2, 10),
        "estimator__learning_rate": trial.suggest_float(
            "learning_rate", 0.01, 0.3, log=True
        ),
        "estimator__subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "estimator__colsample_bytree": trial.suggest_float(
            "colsample_bytree", 0.6, 1.0
        ),
        "estimator__reg_lambda": trial.suggest_float(
            "reg_lambda", 1e-3, 10.0, log=True
        ),
    }


def _space_lightgbm(trial: Any) -> dict[str, Any]:
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 600, step=100),
        "num_leaves": trial.suggest_int("num_leaves", 8, 64),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 40),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
    }


def _space_catboost(trial: Any) -> dict[str, Any]:
    return {
        "iterations": trial.suggest_int("iterations", 100, 600, step=100),
        "depth": trial.suggest_int("depth", 3, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1e-2, 10.0, log=True),
    }


def _space_svc(trial: Any) -> dict[str, Any]:
    return {
        "C": trial.suggest_float("C", 1e-2, 100.0, log=True),
        "gamma": trial.suggest_float("gamma", 1e-4, 1.0, log=True),
        "kernel": trial.suggest_categorical("kernel", ["rbf", "poly", "linear"]),
    }


def _space_knn(trial: Any) -> dict[str, Any]:
    return {
        "n_neighbors": trial.suggest_int("n_neighbors", 3, 25),
        "weights": trial.suggest_categorical("weights", ["uniform", "distance"]),
        "p": trial.suggest_categorical("p", [1, 2]),
    }


def _space_mlp(trial: Any) -> dict[str, Any]:
    hidden = trial.suggest_categorical("hidden_layer_sizes", [(64,), (128,), (64, 32)])
    return {
        "hidden_layer_sizes": hidden,
        "alpha": trial.suggest_float("alpha", 1e-5, 1e-1, log=True),
        "learning_rate_init": trial.suggest_float(
            "learning_rate_init", 1e-4, 1e-2, log=True
        ),
    }


SEARCH_SPACES: dict[str, SearchSpace] = {
    "random_forest": _space_random_forest,
    "extra_trees": _space_extra_trees,
    "gradient_boosting": _space_gradient_boosting,
    "hist_gradient_boosting": _space_hist_gradient_boosting,
    "xgboost": _space_xgboost,
    "lightgbm": _space_lightgbm,
    "catboost": _space_catboost,
    "svc": _space_svc,
    "knn": _space_knn,
    "mlp": _space_mlp,
}


def tunable_models() -> list[str]:
    """Return the models that have a registered search space."""
    return sorted(SEARCH_SPACES)


def tune_model(
    name: str,
    features,
    target,
    n_trials: int = 30,
    folds: int = 5,
    seed: int = 42,
    n_jobs: int = 1,
) -> dict[str, Any]:
    """Tune one model with Optuna and return the best value and parameters."""
    import optuna

    if name not in SEARCH_SPACES:
        raise NotImplementedError(
            f"No search space for '{name}'. Tunable: {tunable_models()}"
        )
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    space = SEARCH_SPACES[name]

    def objective(trial: optuna.Trial) -> float:
        params = {f"clf__{key}": value for key, value in space(trial).items()}
        pipeline = build_pipeline(name, seed, n_jobs)
        pipeline.set_params(**params)
        cv = cross_validate_model(
            pipeline, features, target, folds=folds, seed=seed, n_jobs=n_jobs
        )
        return cv["mean"]

    study = optuna.create_study(
        direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed)
    )
    study.optimize(objective, n_trials=n_trials)
    return {
        "model": name,
        "best_value": float(study.best_value),
        "best_params": dict(study.best_params),
        "n_trials": n_trials,
    }


def tune(
    model_name: str,
    features,
    target,
    n_trials: int = 30,
    seed: int = 42,
    n_jobs: int = 1,
    folds: int = 5,
) -> dict[str, Any]:
    """Backwards-compatible dispatch used by the training pipeline."""
    return tune_model(
        model_name,
        features,
        target,
        n_trials=n_trials,
        folds=folds,
        seed=seed,
        n_jobs=n_jobs,
    )


def tune_grid_random_forest(
    features,
    target,
    folds: int = 5,
    seed: int = 42,
    n_jobs: int = 1,
) -> dict[str, Any]:
    """Exhaustive grid search retained for the quoted Random Forest config."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import GridSearchCV, StratifiedKFold

    from .preprocess import build_tree_preprocessor

    model = Pipeline(
        [
            ("pre", build_tree_preprocessor()),
            (
                "clf",
                RandomForestClassifier(
                    class_weight="balanced", random_state=seed, n_jobs=n_jobs
                ),
            ),
        ]
    )
    grid = {
        "clf__n_estimators": [100, 300, 500],
        "clf__max_depth": [None, 10, 20],
        "clf__min_samples_leaf": [1, 2, 4],
    }
    search = GridSearchCV(
        model,
        grid,
        cv=StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed),
        scoring="f1_macro",
        n_jobs=n_jobs,
    )
    search.fit(features, target)
    return {"best_score": float(search.best_score_), "best_params": search.best_params_}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Tune SEB-XRIF models with Optuna.")
    parser.add_argument(
        "--models",
        nargs="*",
        default=["random_forest", "extra_trees", "xgboost", "lightgbm", "catboost"],
    )
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--cv", type=int, default=5)
    parser.add_argument("--list", action="store_true", help="List tunable models.")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.list:
        print("Tunable models:", ", ".join(tunable_models()))
        return

    settings: Settings = get_settings()
    frame = load_validated(settings=settings)
    features, target = features_and_target(frame, settings)

    results: dict[str, Any] = {}
    for name in args.models:
        print(f"Tuning {name} ({args.trials} trials) ...")
        try:
            result = tune_model(
                name,
                features,
                target,
                n_trials=args.trials,
                folds=args.cv,
                seed=settings.seed,
                n_jobs=settings.n_jobs,
            )
            results[name] = result
            print(f"  {name}: best CV macro F1 = {result['best_value']:.4f}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            results[name] = {"model": name, "status": f"error: {exc}"}
            print(f"  {name}: {exc}")

    out = args.out or (settings.reports_dir / "tuning.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
