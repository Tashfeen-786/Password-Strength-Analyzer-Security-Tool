"""
Password strength scoring engine (PDF section 14).

Score: 0-100. The contributions follow the project PDF:

    + Length:                    up to +35
    + Character diversity:       up to +15
    + Unique-character ratio:    up to +10
    + Pattern resistance:        up to +20
    + Non-common password:       up to +10
    + Additional unpredictability: up to +10

    - Common password:           large penalty (-40)
    - Keyboard sequence:         penalty (-8)
    - Sequential characters:     penalty (-8)
    - Repeated characters:       large penalty (-25)
    - Repeated substring:        penalty (-8, repetition combined cap -25)
    - Personal information:      penalty (-15 each, cap -30)
    - Predictable word+number:   penalty (-8)
    - Predictable word+year:     extra penalty (-6 via year/date)
    - Numeric run:               small penalty (-4)

Total penalty is capped at -45. Final score is capped 0-100.

Classification bands (PROJECT-DEFINED, not universal standards):

      0-20   VERY WEAK
     21-40   WEAK
     41-60   MODERATE
     61-80   STRONG
     81-100  VERY STRONG
"""
from __future__ import annotations

import math

from .length_analyzer import length_score

CLASSIFICATION_BANDS = [
    (81, 100, "VERY STRONG"),
    (61, 80, "STRONG"),
    (41, 60, "MODERATE"),
    (21, 40, "WEAK"),
    (0, 20, "VERY WEAK"),
]

PENALTY_CAP = 45

PENALTIES = {
    "common_password": 40,
    "dictionary_word": 12,
    "leetspeak_substitution": 6,
    "sequential_pattern": 8,
    "keyboard_pattern": 8,
    "repeated_characters": 25,
    "repeated_substring": 8,
    "predictable_structure": 8,
    "year_date_pattern": 6,
    "numeric_run": 4,
    "personal_info_name": 15,
    "personal_info_org": 15,
    "personal_info_year": 15,
}

_PATTERN_RESISTANCE_CATEGORIES = {
    "sequential_pattern", "keyboard_pattern", "repeated_characters",
    "repeated_substring", "predictable_structure", "year_date_pattern",
}


def classify_score(score: int | float) -> str:
    """Map a 0-100 score onto the project-defined classification bands."""
    score = int(round(score))
    for low, high, label in CLASSIFICATION_BANDS:
        if low <= score <= high:
            return label
    return "VERY WEAK"


def _unpredictability(pool_size: int, unique_ratio: float,
                      pattern_types: set[str]) -> int:
    """Heuristic 0-10 bonus based on per-character pool entropy discounted
    by the unique-character ratio. Capped at 4 when obvious patterns exist."""
    if pool_size <= 1 or unique_ratio <= 0:
        return 0
    per_char = math.log2(pool_size) * unique_ratio
    if per_char >= 4.5:
        value = 10
    elif per_char >= 3.5:
        value = 7
    elif per_char >= 2.5:
        value = 4
    else:
        value = 1
    if pattern_types & {"sequential_pattern", "keyboard_pattern",
                        "repeated_characters", "repeated_substring"}:
        value = min(value, 4)
    return value


def compute_score(*, length: int, character_type_count: int,
                  unique_character_ratio: float, pool_size: int,
                  findings: list[dict], is_common: bool,
                  dictionary_hit: bool, breach_found: bool,
                  dictionary_penalty: int | None = None) -> dict:
    """Compute the 0-100 score, a transparent breakdown, and classification.

    All inputs are derived metrics — never the password itself.
    """
    pattern_types = {f["type"] for f in findings}

    contributions = {
        "length": length_score(length),
        "character_diversity": int(15 * min(character_type_count, 4) / 4),
        "unique_character_ratio": min(10, round(unique_character_ratio * 10)),
        "pattern_resistance": max(
            0, 20 - 5 * len(pattern_types & _PATTERN_RESISTANCE_CATEGORIES)),
        "non_common_password": 0 if (is_common or dictionary_hit) else 10,
        "unpredictability": _unpredictability(pool_size, unique_character_ratio,
                                              pattern_types),
    }
    base = sum(contributions.values())

    applied: dict[str, int] = {}
    repetition_total = 0
    personal_total = 0
    for f in findings:
        ftype = f["type"]
        if ftype in ("repeated_characters", "repeated_substring"):
            repetition_total += PENALTIES[ftype]
            applied[ftype] = PENALTIES[ftype]
        elif ftype.startswith("personal_info"):
            personal_total += PENALTIES[ftype]
            applied[ftype] = PENALTIES[ftype]
        elif ftype in PENALTIES and ftype not in ("common_password",
                                                  "dictionary_word"):
            # common / dictionary penalties are applied once below via flags.
            applied[ftype] = applied.get(ftype, 0) + PENALTIES[ftype]

    # Re-substitute capped group totals.
    if repetition_total:
        capped = min(repetition_total, 25)
        for key in ("repeated_characters", "repeated_substring"):
            applied.pop(key, None)
        applied["repetition"] = capped
    if personal_total:
        capped = min(personal_total, 30)
        for key in ("personal_info_name", "personal_info_org",
                    "personal_info_year"):
            applied.pop(key, None)
        applied["personal_information"] = capped

    if is_common:
        applied["common_password"] = PENALTIES["common_password"]
    if dictionary_hit:
        applied["dictionary_word"] = (dictionary_penalty
                                      if dictionary_penalty is not None
                                      else PENALTIES["dictionary_word"])

    total_penalty = min(sum(applied.values()), PENALTY_CAP)

    score = max(0, min(100, base - total_penalty))

    # Hard severity caps (project-defined teaching rules):
    #  * an exact common-password match is ALWAYS very weak, no matter how
    #    long it looks ('aaaaaaaa' still loses to 'it's in the top lists').
    #  * a demo breach-corpus hit caps the score at the bottom of the scale.
    #  * very short inputs can never escape the weakest bands.
    if is_common:
        score = min(score, 15)
    if breach_found:
        score = min(score, 10)
    if length < 4:
        score = min(score, 15)
    elif length < 8:
        score = min(score, 25)

    # Single-character-class cap: a password drawn from one small pool
    # (only digits, only lowercase...) is predictable even at moderate length.
    if character_type_count == 1:
        if length < 14:
            score = min(score, 40)
        elif length < 20:
            score = min(score, 60)

    return {
        "score": score,
        "classification": classify_score(score),
        "contributions": contributions,
        "penalties": applied,
        "total_penalty": total_penalty,
        "breach_cap_applied": breach_found,
        "note": ("Project-defined scoring bands for education — not a "
                 "universal security standard."),
    }
