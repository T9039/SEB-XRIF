"""Preprocessing pipeline builders.

Two column transformers are provided: one for tree ensembles (no scaling) and
one for scale-sensitive estimators (SVM, KNN, MLP). Both are intended to be
composed inside a single scikit-learn `Pipeline` so preprocessing travels with
the serialized model.

The categorical and numeric column lists default to the Kalboard schema but can
be supplied per source, so a dataset with a different feature set (e.g. the XR
engagement frame, which is all numeric) trains through the same builders.
"""

from __future__ import annotations

from collections.abc import Sequence

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .schema import BEHAVIOURAL, CATEGORICAL


def _transformers(
    categorical: Sequence[str], numeric: Sequence[str], scale: bool
) -> list[tuple[str, object, list[str]]]:
    transformers: list[tuple[str, object, list[str]]] = []
    if categorical:
        transformers.append(
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(categorical),
            )
        )
    if numeric:
        transformers.append(
            ("num", StandardScaler() if scale else "passthrough", list(numeric))
        )
    return transformers


def build_tree_preprocessor(
    categorical: Sequence[str] | None = None,
    numeric: Sequence[str] | None = None,
) -> ColumnTransformer:
    """One-hot encode categoricals; pass behavioural counts through unscaled."""
    categorical = CATEGORICAL if categorical is None else categorical
    numeric = BEHAVIOURAL if numeric is None else numeric
    return ColumnTransformer(_transformers(categorical, numeric, scale=False))


def build_scaled_preprocessor(
    categorical: Sequence[str] | None = None,
    numeric: Sequence[str] | None = None,
) -> ColumnTransformer:
    """One-hot encode categoricals and standardise behavioural counts."""
    categorical = CATEGORICAL if categorical is None else categorical
    numeric = BEHAVIOURAL if numeric is None else numeric
    return ColumnTransformer(_transformers(categorical, numeric, scale=True))
