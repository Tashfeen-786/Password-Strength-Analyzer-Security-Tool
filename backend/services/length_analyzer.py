"""
Length analysis (PDF section 5).

Educational length bands (configurable guidance):

    < 8       : Very short
    8 - 11    : Short
    12 - 15   : Better length
    16 +      : Strong length contribution

NOTE: length alone never makes a password secure.
``aaaaaaaaaaaaaaaaaaaa`` is long but highly predictable — pattern analysis
must run alongside length analysis.
"""
from __future__ import annotations

BANDS = [
    (16, "Strong length contribution"),
    (12, "Better length"),
    (8, "Short"),
    (1, "Very short"),
    (0, "Empty"),
]


def analyze_length(password: str) -> dict:
    """Classify the password length into its educational band."""
    length = len(password)
    for minimum, label in BANDS:
        if length >= minimum:
            band = label
            break
    return {
        "length": length,
        "band": band,
        "meets_recommended_minimum_12": length >= 12,
        "meets_strong_threshold_16": length >= 16,
        "note": "Length alone does not make a password secure.",
    }


# Length scoring contribution used by the scoring engine (max +35 points).
def length_score(length: int) -> int:
    if length >= 16:
        return 35
    if length >= 12:
        return 28
    if length >= 8:
        return 22
    if length >= 4:
        return 8
    if length >= 1:
        return 2
    return 0
