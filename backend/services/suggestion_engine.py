"""
Security suggestion engine (PDF section 15).

Suggestions must be SPECIFIC and actionable. They never contain, echo, or
reveal the submitted password.

  BAD:  "Make your password stronger."
  GOOD: "Your password contains a predictable numeric sequence."
"""
from __future__ import annotations

_TYPE_SUGGESTIONS: dict[str, list[str]] = {
    "common_password": [
        "Do not use this password — it appears in common-password lists that "
        "attackers try first.",
        "Choose a unique password that is not based on any common pattern.",
    ],
    "breach_exposure": [
        "Never reuse a password that has appeared in a breach (demo detection). "
        "Change it everywhere it may have been used.",
    ],
    "dictionary_word": [
        "Avoid common dictionary words; combine unrelated words in a "
        "passphrase instead.",
    ],
    "sequential_pattern": [
        "Your password contains a predictable sequence of characters — remove "
        "runs like ascending or descending letters/numbers.",
    ],
    "keyboard_pattern": [
        "Avoid common keyboard sequences such as 'qwerty' — attackers test "
        "them immediately.",
    ],
    "repeated_characters": [
        "Remove long runs of the same character; repetition drastically "
        "reduces unpredictability.",
    ],
    "repeated_substring": [
        "Avoid repeating the same chunk of characters inside your password.",
    ],
    "predictable_structure": [
        "A common word followed by numbers or a year is highly predictable — "
        "adding a predictable number to a common word does not make it strong.",
    ],
    "year_date_pattern": [
        "Avoid years and dates (birthdays, anniversaries) — they are "
        "frequently targeted guesses.",
    ],
    "numeric_run": [
        "Avoid long runs of digits such as PIN- or phone-like fragments.",
    ],
    "personal_info_name": [
        "Avoid including your name in passwords — it is one of the first "
        "things attackers try.",
    ],
    "personal_info_year": [
        "Avoid including your birth year in passwords.",
    ],
    "personal_info_org": [
        "Avoid including your company or college name in passwords.",
    ],
}

_GENERAL = {
    "short": "Use a longer password or passphrase — aim for 12-16+ characters.",
    "good_length": None,  # positive signal, no suggestion needed
    "low_diversity": "Add variety: UPPERCASE, lowercase, digits, and symbols.",
}


def generate_suggestions(*, findings: list[dict], length: int,
                         character_type_count: int) -> list[str]:
    """Build the final, de-duplicated, specific suggestion list.

    Input is derived findings/metrics only — never the password.
    """
    suggestions: list[str] = []
    types = {f["type"] for f in findings}

    for ftype in [f["type"] for f in findings]:
        for text in _TYPE_SUGGESTIONS.get(ftype, []):
            if text not in suggestions:
                suggestions.append(text)

    if length < 12:
        suggestions.append(_GENERAL["short"])
    if 0 < character_type_count < 3:
        suggestions.append(_GENERAL["low_diversity"])

    # Standing good-practice guidance (always relevant, PDF section 15).
    suggestions.extend([
        "Avoid reusing passwords across different accounts.",
        "Use a password manager to generate and store unique passwords.",
        "Enable MFA (multi-factor authentication) wherever it is available.",
    ])
    return list(dict.fromkeys(suggestions))
