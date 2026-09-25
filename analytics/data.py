"""Dataset IO, validation, and splitting.

The single entry point for turning the raw CSV into validated features and a
stratified train/test split. Used by training, tuning, and the DVC pipeline.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from .config import Settings, get_settings
from .datasets.base import Dataset
from .datasets.kalboard import KalboardAdapter
from .datasets.registry import get_adapter

_kalboard = KalboardAdapter()


def load_raw(
    path: Path | str | None = None, settings: Settings | None = None
) -> pd.DataFrame:
    """Load the raw learner table from CSV."""
    return _kalboard.load_raw(path, settings)


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Validate the table against the pandera schema, returning a coerced copy."""
    return _kalboard.validate(df)


def load_validated(
    path: Path | str | None = None, settings: Settings | None = None
) -> pd.DataFrame:
    """Load and validate the dataset in one call."""
    return validate(load_raw(path, settings))


def read_learners(
    settings: Settings | None = None, prefer_db: bool = True
) -> tuple[pd.DataFrame, str]:
    """Return a validated feature frame and its source.

    Prefers the application database when it holds learners, and falls back to
    the bundled CSV. The returned source is ``"database"`` or ``"csv"``.
    """
    return _kalboard.read_learners(settings, prefer_db)


def load_dataset(settings: Settings | None = None) -> Dataset:
    """Return the configured dataset (frame + features + target) via its adapter."""
    settings = settings or get_settings()
    return get_adapter(settings.dataset, settings).load(settings)


def load_source(settings: Settings | None = None) -> tuple[pd.DataFrame, str]:
    """Return ``(frame, source)`` for the configured dataset (``settings.dataset``)."""
    dataset = load_dataset(settings)
    return dataset.frame, dataset.source


def features_and_target(
    df: pd.DataFrame, settings: Settings | None = None
) -> tuple[pd.DataFrame, pd.Series]:
    """Split a validated table into the 16 predictors and the target."""
    settings = settings or get_settings()
    features = df[settings.feature_columns].copy()
    target = df[settings.target].copy()
    return features, target


def split(
    features: pd.DataFrame, target: pd.Series, settings: Settings | None = None
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Return a stratified train/test split with the configured seed."""
    settings = settings or get_settings()
    return train_test_split(
        features,
        target,
        test_size=settings.test_size,
        random_state=settings.seed,
        stratify=target,
    )


def class_distribution(target: pd.Series) -> dict[str, int]:
    """Return the count of each performance tier."""
    return {str(label): int(count) for label, count in target.value_counts().items()}


def main(argv: list[str] | None = None) -> None:
    """Validate the raw data and write the processed table (DVC prepare stage)."""
    parser = argparse.ArgumentParser(description="Prepare and validate the dataset.")
    parser.add_argument("--out", type=Path, default=None, help="Output parquet path.")
    args = parser.parse_args(argv)

    settings = get_settings()
    out_path = args.out or settings.processed_path
    df = load_validated(settings=settings)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    print(f"Validated {len(df)} rows -> {out_path}")
    print(f"Class distribution: {class_distribution(df[settings.target])}")


if __name__ == "__main__":
    main()
