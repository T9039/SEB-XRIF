"""Support-band mapping, decision thresholds, calibration, and CV intervals."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

from analytics.decision import apply_thresholds, support_band
from analytics.diagnostics import expected_calibration_error
from analytics.evaluate import cross_validate_model


def test_support_band_default_and_custom():
    assert support_band("L") == "priority-support"
    assert support_band("M") == "monitor"
    assert support_band("H") == "on-track"
    assert support_band("X", {"X": "bespoke"}) == "bespoke"
    assert support_band("Z") == "Z"


def test_apply_thresholds_defaults_to_argmax():
    probabilities = np.array([[0.6, 0.3, 0.1], [0.2, 0.5, 0.3]])
    assert apply_thresholds(probabilities, ["L", "M", "H"]) == ["L", "M"]


def test_threshold_promotes_the_support_class():
    # Row 2's argmax is M, but P(L) clears the support threshold so it is
    # flagged for priority support (the cost-sensitive trade).
    probabilities = np.array([[0.30, 0.50, 0.20], [0.36, 0.40, 0.24]])
    assert apply_thresholds(probabilities, ["L", "M", "H"]) == ["M", "M"]
    assert apply_thresholds(probabilities, ["L", "M", "H"], {"L": 0.35}) == ["M", "L"]


def test_apply_thresholds_validates_shape():
    with pytest.raises(ValueError):
        apply_thresholds(np.array([0.1, 0.9]), ["L", "H"])
    with pytest.raises(ValueError):
        apply_thresholds(np.array([[0.5, 0.5]]), ["L", "M", "H"])


def test_expected_calibration_error():
    assert expected_calibration_error(
        np.array([1, 1, 1]), np.array([1.0, 1.0, 1.0])
    ) == pytest.approx(0.0)
    assert expected_calibration_error(
        np.array([0, 0]), np.array([1.0, 1.0])
    ) == pytest.approx(1.0)
    assert expected_calibration_error(
        np.array([0, 0]), np.array([0.5, 0.5])
    ) == pytest.approx(0.5)


def test_cross_validation_reports_confidence_interval():
    features, target = make_classification(
        n_samples=150,
        n_features=5,
        n_informative=4,
        n_redundant=0,
        n_classes=3,
        n_clusters_per_class=1,
        random_state=0,
    )
    cv = cross_validate_model(
        LogisticRegression(max_iter=500), features, target, folds=5, seed=0
    )
    assert cv["ci_low"] <= cv["mean"] <= cv["ci_high"]
    assert cv["stderr"] >= 0.0
    assert cv["ci_level"] == 0.95
    assert len(cv["scores"]) == 5
