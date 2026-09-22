"""Tests for preprocessing and splitting."""

from __future__ import annotations

from analytics.data import features_and_target, load_validated, split
from analytics.preprocess import build_scaled_preprocessor, build_tree_preprocessor
from analytics.schema import BEHAVIOURAL, CATEGORICAL


def test_tree_preprocessor_one_hot_encodes():
    df = load_validated()
    features, _ = features_and_target(df)
    transformed = build_tree_preprocessor().fit_transform(features)
    assert transformed.shape[0] == len(features)
    assert transformed.shape[1] >= len(CATEGORICAL) + len(BEHAVIOURAL)


def test_scaled_preprocessor_produces_float_output():
    df = load_validated()
    features, _ = features_and_target(df)
    pre = build_scaled_preprocessor()
    transformed = pre.fit_transform(features)
    assert transformed.shape[0] == len(features)


def test_feature_names_are_available():
    df = load_validated()
    features, _ = features_and_target(df)
    pre = build_tree_preprocessor()
    pre.fit(features)
    assert len(pre.get_feature_names_out()) == pre.transform(features).shape[1]


def test_split_is_stratified_and_sized():
    df = load_validated()
    features, target = features_and_target(df)
    x_train, x_test, y_train, y_test = split(features, target)
    total = len(x_train) + len(x_test)
    assert total == 480
    assert len(x_test) == 96
    # Stratification keeps class proportions close.
    train_ratio = y_train.value_counts(normalize=True)
    test_ratio = y_test.value_counts(normalize=True)
    assert (train_ratio - test_ratio).abs().max() < 0.05
