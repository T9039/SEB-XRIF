"""Effect-size calculation for learning outcomes.

Primary path uses pingouin (note: GPL-3.0). A scipy/NumPy fallback is provided
so the framework can be redistributed without the copyleft dependency; see the
license flag in specification section 3.5.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np


def cohens_d(group_a: Sequence[float], group_b: Sequence[float],
             paired: bool = False) -> float:
    """Return Cohen's d between two groups.

    Args:
        group_a: first set of observations.
        group_b: second set of observations.
        paired: use the paired (d_avg) formula.
    """
    if paired:
        return _cohens_d_paired(group_a, group_b)
    return _cohens_d_independent(group_a, group_b)


def _cohens_d_independent(a: Sequence[float], b: Sequence[float]) -> float:
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    n1, n2 = x.size, y.size
    pooled_var = ((n1 - 1) * x.var(ddof=1) + (n2 - 1) * y.var(ddof=1)) / (
        n1 + n2 - 2
    )
    return float((x.mean() - y.mean()) / np.sqrt(pooled_var))


def _cohens_d_paired(a: Sequence[float], b: Sequence[float]) -> float:
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    pooled_sd = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
    return float((x.mean() - y.mean()) / pooled_sd)
