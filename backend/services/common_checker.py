"""
Common password & dictionary word detection (PDF sections 7 and 7/7.x).

Uses small, local, educational lists loaded from data/. No external calls.
If a password matches a commonly used password, the user is told:

    "Your password matches a commonly used password pattern and should
     not be used."
"""
from __future__ import annotations

import re

from ..utils.config import COMMON_PASSWORDS_FILE, DICTIONARY_WORDS_FILE


def load_word_set(path: str) -> set[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return {line.strip().lower() for line in fh if line.strip()}
    except OSError:
        return set()


COMMON_PASSWORDS: set[str] = load_word_set(COMMON_PASSWORDS_FILE)
DICTIONARY_WORDS: set[str] = load_word_set(DICTIONARY_WORDS_FILE)

# Leetspeak substitution map used for the normalized comparison pass.
# 'P@ssw0rd99' normalizes to 'password99' — a predictable variant.
LEET_MAP = str.maketrans({
    "@": "a", "0": "o", "1": "l", "3": "e", "4": "a",
    "5": "s", "7": "t", "8": "b", "$": "s", "!": "i", "+": "t",
})


def normalize_leet(password: str) -> str:
    """Lower-cased leetspeak-normalized form (may equal the original)."""
    return password.lower().translate(LEET_MAP)


def leetspeak_finding() -> dict:
    return {
        "type": "leetspeak_substitution",
        "severity": "medium",
        "title": "Leetspeak substitution detected",
        "description": "Password uses letter-for-symbol substitutions that "
                       "reduce to a predictable word.",
        "detail": ("Replacing letters with look-alike symbols (a->@, o->0, "
                   "e->3...) is a well-known trick that cracking rules apply "
                   "automatically."),
    }


def is_common_password(password: str, common: set[str] | None = None) -> bool:
    """True if the password (case-insensitively) is a known common password."""
    common = common if common is not None else COMMON_PASSWORDS
    return password.lower() in common


def find_dictionary_words(password: str, words: set[str] | None = None,
                          min_len: int = 4) -> list[str]:
    """Return dictionary words (len >= min_len) detected in the password.

    Two passes:
      1. split on separators/digits and match whole parts (fast, precise)
      2. substring scan of the whole string for words of len >= min_len
         (catches concatenations like 'monkeybusiness')
    """
    words = words if words is not None else DICTIONARY_WORDS
    lowered = password.lower()
    parts = re.split(r"[^a-z]+", lowered)
    hits = {p for p in parts if len(p) >= min_len and p in words}
    if lowered and len(lowered) <= 128:
        for word in words:
            if len(word) >= min_len and word in lowered:
                hits.add(word)
    return sorted(hits)


def common_password_finding() -> dict:
    return {
        "type": "common_password",
        "severity": "critical",
        "title": "Common password detected",
        "description": "Password matches a commonly used password.",
        "detail": ("Your password matches a commonly used password pattern "
                   "and should not be used."),
    }


def dictionary_finding(words: list[str]) -> dict:
    return {
        "type": "dictionary_word",
        "severity": "medium",
        "title": "Dictionary word detected",
        "description": "Password contains common dictionary word(s).",
        "detail": ("Contains the common word(s) "
                   + ", ".join(f"'{w}'" for w in words[:3])
                   + ". Dictionary words make passwords predictable."),
        "word_count": len(words),
    }
