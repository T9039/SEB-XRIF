"""System Usability Scale (SUS) scoring.

Ten items rated 1-5. Odd-numbered items are positively worded, even-numbered
items negatively worded. Each item contributes 0-4 points; the total is
multiplied by 2.5 to give a score out of 100.
"""
from __future__ import annotations

from typing import Sequence


def sus_score(responses: Sequence[int]) -> float:
    """Return the SUS score (0-100) for ten Likert responses.

    Raises:
        ValueError: if the response count is not ten or any value is outside
            1-5.
    """
    if len(responses) != 10:
        raise ValueError("SUS requires exactly 10 responses")
    if any(r < 1 or r > 5 for r in responses):
        raise ValueError("SUS responses must be between 1 and 5")

    odd = sum(responses[i] - 1 for i in range(0, 10, 2))
    even = sum(5 - responses[i] for i in range(1, 10, 2))
    return (odd + even) * 2.5
