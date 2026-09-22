"""Hyperparameter tuning.

Optuna (TPE with median pruning) is the default search strategy. GridSearchCV
is retained for the Random Forest so the configuration quoted in the paper is
exactly reproducible. See the technical specification, section 4.6.
"""

from __future__ import annotations

from typing import Any

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

from .preprocess import build_tree_preprocessor


def _cv(folds: int, seed: int) -> StratifiedKFold:
    return StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)


def tune_random_forest(
    features,
    target,
    n_trials: int = 50,
    folds: int = 5,
    seed: int = 42,
    n_jobs: int = 1,
) -> dict[str, Any]:
    """Tune the Random Forest with Optuna and return the best parameters."""
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 600, step=100),
            "max_depth": trial.suggest_int("max_depth", 2, 30),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
            "max_features": trial.suggest_categorical(
                "max_features", ["sqrt", "log2", None]
            ),
        }
        model = Pipeline(
            [
                ("pre", build_tree_preprocessor()),
                (
                    "clf",
                    RandomForestClassifier(
                        class_weight="balanced",
                        random_state=seed,
                        n_jobs=n_jobs,
                        **params,
                    ),
                ),
            ]
        )
        scores = cross_val_score(
            model,
            features,
            target,
            cv=_cv(folds, seed),
            scoring="f1_macro",
            n_jobs=n_jobs,
        )
        return float(scores.mean())

    study = optuna.create_study(
        direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed)
    )
    study.optimize(objective, n_trials=n_trials)
    return {
        "best_value": float(study.best_value),
        "best_params": study.best_params,
        "n_trials": n_trials,
    }


def tune_grid_random_forest(
    features,
    target,
    folds: int = 5,
    seed: int = 42,
    n_jobs: int = 1,
) -> dict[str, Any]:
    """Exhaustive grid search for the Random Forest configuration."""
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
        cv=_cv(folds, seed),
        scoring="f1_macro",
        n_jobs=n_jobs,
    )
    search.fit(features, target)
    return {
        "best_score": float(search.best_score_),
        "best_params": search.best_params_,
    }


def tune(
    model_name: str,
    features,
    target,
    n_trials: int = 50,
    seed: int = 42,
    n_jobs: int = 1,
):
    """Dispatch tuning by model name. Extend as search spaces are added."""
    if model_name == "random_forest":
        return tune_random_forest(
            features, target, n_trials=n_trials, seed=seed, n_jobs=n_jobs
        )
    raise NotImplementedError(
        f"Tuning for '{model_name}' is not implemented; "
        "add a search space in analytics/tune.py."
    )
