"""Tests for the evaluation layer."""
from __future__ import annotations

import pytest

from eval.effect_size import cohens_d
from eval.sus import sus_score


def test_sus_perfect_score():
    assert sus_score([5, 1, 5, 1, 5, 1, 5, 1, 5, 1]) == 100.0


def test_sus_minimum_score():
    assert sus_score([1, 5, 1, 5, 1, 5, 1, 5, 1, 5]) == 0.0


def test_sus_neutral_score():
    assert sus_score([3] * 10) == 50.0


def test_sus_rejects_wrong_length():
    with pytest.raises(ValueError):
        sus_score([3] * 9)


def test_sus_rejects_out_of_range():
    with pytest.raises(ValueError):
        sus_score([6, 1, 1, 1, 1, 1, 1, 1, 1, 1])


def test_cohens_d_zero_when_identical():
    assert cohens_d([1, 2, 3, 4], [1, 2, 3, 4]) == 0.0


def test_cohens_d_sign_and_magnitude():
    d = cohens_d([5, 6, 7, 8, 9], [1, 2, 3, 4, 5])
    assert d > 0
    assert d > 1.0


def test_cohens_d_paired_runs():
    d = cohens_d([2, 3, 4], [1, 1, 1], paired=True)
    assert d > 0
