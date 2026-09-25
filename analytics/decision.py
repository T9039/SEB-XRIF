"""Support-band mapping and cost-sensitive decision thresholds.

The model predicts a Low/Medium/High academic band. For early support the
output is reframed as an actionable **support band**, and the decision rule can
flag a class at a probability below the argmax — trading some precision for
recall on the band that matters (priority support), which is the point of an
early-warning system.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np

#: Fallback band names when configuration does not supply them.
DEFAULT_BANDS: dict[str, str] = {
    "L": "priority-support",
    "M": "monitor",
    "H": "on-track",
}


def support_band(label: str, bands: Mapping[str, str] | None = None) -> str:
    """Map a predicted class label onto its support band name."""
    mapping = bands or DEFAULT_BANDS
    return str(mapping.get(str(label), str(label)))


def apply_thresholds(
    probabilities: np.ndarray | Sequence[Sequence[float]],
    classes: Sequence[str],
    thresholds: Mapping[str, float] | None = None,
) -> list[str]:
    """Return predictions, flagging a class when its probability clears its threshold.

    Each threshold raises the likelihood that its class is predicted: if
    ``P(class) >= threshold`` the row is assigned that class, otherwise the
    argmax wins. With no thresholds this is plain argmax.
    """
    proba = np.asarray(probabilities, dtype=float)
    if proba.ndim != 2:
        raise ValueError("probabilities must be a 2-D array of shape (n, classes)")
    class_list = [str(label) for label in classes]
    if proba.shape[1] != len(class_list):
        raise ValueError("probability columns must match the number of classes")

    predictions = [class_list[index] for index in np.argmax(proba, axis=1)]
    for label, threshold in (thresholds or {}).items():
        if label not in class_list:
            continue
        column = class_list.index(label)
        for row, probability in enumerate(proba[:, column]):
            if probability >= float(threshold):
                predictions[row] = label
    return predictions
