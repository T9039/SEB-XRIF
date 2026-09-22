"""Preprocessing pipeline builders.

Two column transformers are provided: one for tree ensembles (no scaling) and
one for scale-sensitive estimators (SVM, KNN, MLP). Both are intended to be
composed inside a single scikit-learn `Pipeline` so preprocessing travels with
the serialized model.
"""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .schema import BEHAVIOURAL, CATEGORICAL


def build_tree_preprocessor() -> ColumnTransformer:
    """One-hot encode categoricals; pass behavioural counts through unscaled."""
    return ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", BEHAVIOURAL),
        ]
    )


def build_scaled_preprocessor() -> ColumnTransformer:
    """One-hot encode categoricals and standardise behavioural counts."""
    return ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", StandardScaler(), BEHAVIOURAL),
        ]
    )
