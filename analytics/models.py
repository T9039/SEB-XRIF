"""Model catalog for the full comparison matrix.

Every estimator in the technical specification's comparison matrix is
registered here and built through a single factory so that each model gets the
same preprocessing, seed, and interface. Optional libraries (XGBoost,
LightGBM, CatBoost) are imported lazily inside their factories so the module
still imports when they are absent.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    StackingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from .preprocess import build_scaled_preprocessor, build_tree_preprocessor

# Estimators that require standardised inputs (ensembles contain scale-sensitive
# base learners, so they are standardised too).
SCALE_SENSITIVE = {
    "logistic_regression",
    "svc",
    "knn",
    "mlp",
    "voting",
    "stacking",
}


def _dummy(seed: int) -> Any:
    return DummyClassifier(strategy="most_frequent")


def _logistic_regression(seed: int) -> Any:
    return LogisticRegression(max_iter=1000, random_state=seed)


def _decision_tree(seed: int) -> Any:
    return DecisionTreeClassifier(random_state=seed)


def _naive_bayes(seed: int) -> Any:
    return GaussianNB()


def _random_forest(seed: int) -> Any:
    return RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=seed,
        n_jobs=-1,
    )


def _extra_trees(seed: int) -> Any:
    return ExtraTreesClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=seed,
        n_jobs=-1,
    )


def _gradient_boosting(seed: int) -> Any:
    return GradientBoostingClassifier(random_state=seed)


def _hist_gradient_boosting(seed: int) -> Any:
    return HistGradientBoostingClassifier(random_state=seed)


def _svc(seed: int) -> Any:
    return SVC(probability=True, random_state=seed)


def _knn(seed: int) -> Any:
    return KNeighborsClassifier(n_neighbors=5)


def _mlp(seed: int) -> Any:
    return MLPClassifier(random_state=seed, max_iter=500)


def _xgboost(seed: int) -> Any:
    from xgboost import XGBClassifier

    return XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=seed,
        n_jobs=-1,
    )


def _lightgbm(seed: int) -> Any:
    from lightgbm import LGBMClassifier

    return LGBMClassifier(
        n_estimators=300,
        learning_rate=0.1,
        random_state=seed,
        n_jobs=-1,
        verbose=-1,
    )


def _catboost(seed: int) -> Any:
    from catboost import CatBoostClassifier

    return CatBoostClassifier(
        iterations=300,
        learning_rate=0.1,
        random_seed=seed,
        verbose=0,
    )


def _voting(seed: int) -> Any:
    return VotingClassifier(
        estimators=[
            ("rf", _random_forest(seed)),
            ("svc", SVC(probability=True, random_state=seed)),
            ("lr", LogisticRegression(max_iter=1000, random_state=seed)),
        ],
        voting="soft",
    )


def _stacking(seed: int) -> Any:
    return StackingClassifier(
        estimators=[
            ("rf", _random_forest(seed)),
            ("et", _extra_trees(seed)),
            ("svc", SVC(probability=True, random_state=seed)),
        ],
        final_estimator=LogisticRegression(max_iter=1000, random_state=seed),
        n_jobs=-1,
    )


MODEL_FACTORIES: dict[str, Callable[[int], Any]] = {
    "dummy": _dummy,
    "logistic_regression": _logistic_regression,
    "decision_tree": _decision_tree,
    "naive_bayes": _naive_bayes,
    "random_forest": _random_forest,
    "extra_trees": _extra_trees,
    "gradient_boosting": _gradient_boosting,
    "hist_gradient_boosting": _hist_gradient_boosting,
    "svc": _svc,
    "knn": _knn,
    "xgboost": _xgboost,
    "lightgbm": _lightgbm,
    "catboost": _catboost,
    "voting": _voting,
    "stacking": _stacking,
    "mlp": _mlp,
}


def model_catalog() -> list[str]:
    """Return the names of every registered model."""
    return sorted(MODEL_FACTORIES)


def build_estimator(name: str, seed: int = 42) -> Any:
    """Build a bare estimator by name."""
    if name not in MODEL_FACTORIES:
        raise KeyError(f"Unknown model '{name}'. Known: {model_catalog()}")
    return MODEL_FACTORIES[name](seed)


def build_pipeline(name: str, seed: int = 42) -> Pipeline:
    """Wrap an estimator with the appropriate preprocessing pipeline."""
    pre = (
        build_scaled_preprocessor()
        if name in SCALE_SENSITIVE
        else build_tree_preprocessor()
    )
    return Pipeline([("pre", pre), ("clf", build_estimator(name, seed))])
