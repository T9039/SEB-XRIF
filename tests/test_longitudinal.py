"""Tests for the longitudinal evaluation protocol."""

from __future__ import annotations

import pytest

from eval.longitudinal import Measurement, summarise, validate_time_point


def test_validate_time_point():
    assert validate_time_point("T0") == "T0"
    with pytest.raises(ValueError):
        validate_time_point("T3")


def test_measurement_rejects_bad_time_point():
    with pytest.raises(ValueError):
        Measurement(learner_id="a", time_point="T9", score=1.0)


def test_summarise_immediate_only():
    result = summarise(t0=[1, 2, 3], t1=[3, 4, 5])
    assert result["n"] == 3
    assert result["gain_immediate"] == pytest.approx(2.0)
    assert result["d_immediate"] > 0


def test_summarise_with_retention():
    result = summarise(t0=[1, 2, 3], t1=[5, 6, 7], t2=[3, 4, 5])
    assert result["gain_delayed"] == pytest.approx(2.0)
    assert result["decay_t2_t1"] == pytest.approx(-2.0)
    # Retained 2 of the 4 immediate points -> ratio 0.5.
    assert result["retention_ratio"] == pytest.approx(0.5)


def test_summarise_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        summarise(t0=[1, 2], t1=[3])
