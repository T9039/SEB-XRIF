"""Training entrypoint.

Phase 3 builds and evaluates the proposed Random Forest. Phase 4 extends this
into the full comparison matrix (see specification section 4.4).
"""
from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from .preprocess import build_tree_preprocessor

DEFAULT_SEED = 42


def build_random_forest(seed: int = DEFAULT_SEED) -> Pipeline:
    """Return the proposed Random Forest pipeline (100 trees, balanced)."""
    return Pipeline(
        [
            ("pre", build_tree_preprocessor()),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=100,
                    class_weight="balanced",
                    random_state=seed,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def main() -> None:
    raise NotImplementedError(
        "Matrix runner is implemented in build-plan phases 3-4."
    )


if __name__ == "__main__":
    main()
