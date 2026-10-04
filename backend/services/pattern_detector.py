"""
Pattern detection (PDF sections 8, 9, 10, 11).

Detects:
  * sequential numbers    (1234, 5678)  + ascending
  * sequential letters    (abcd, bcde)  + e.g. 9876, dcba (descending)
  * keyboard patterns     (qwerty, asdf, zxcv, 1qaz2wsx)
  * repeated characters   (aaaa, 1111)
  * repeated substrings   (ababab, abcabcabc)
  * year/date-like patterns (1998, 2026, 2026-07-15)
  * predictable word + number structure (welcome123, admin2026)

Every finding carries a *generic* ``type``/``description`` (safe to persist
in analytics storage) plus a transient ``detail`` that is returned to the to
the same session that submitted the password and never stored.
"""
from __future__ import annotations

import re
from typing import Optional

# QWERTY keyboard letter rows. (The number row is intentionally excluded:
# '1234' is already caught by detect_sequences().)
KEYBOARD_ROWS = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
]

# Common diagonal/columnar keyboard walks (e.g. 1qaz2wsx). Minimum length 3
# to avoid false positives on ordinary two-letter adjacencies.
KEYBOARD_WALKS = [
    "1qaz", "2wsx", "3edc", "4rfv", "5tgb", "6yhn", "7ujm",
    "qaz", "wsx", "edc", "rfv", "tgb", "yhn", "ujm", "zaq", "xsw",
]

MIN_SEQUENCE_RUN = 3  # shortest ascending/descending run we flag


def _runs(s: str) -> list[str]:
    """All ascending alphabetic/numeric runs of length >= MIN_SEQUENCE_RUN."""
    found = []
    lower = s.lower()
    i = 0
    while i <= len(lower) - MIN_SEQUENCE_RUN:
        run = 1
        while (i + run < len(lower)
               and lower[i + run].isalnum()
               and ord(lower[i + run]) - ord(lower[i + run - 1]) == 1):
            run += 1
        if run >= MIN_SEQUENCE_RUN:
            found.append(lower[i:i + run])
            i += run
        else:
            i += 1
    return found


def detect_sequences(password: str) -> Optional[dict]:
    """Detect ascending or descending sequential runs (numbers or letters)."""
    ascending = _runs(password)
    # Find descending runs by scanning the reversed string, then reverse the
    # matched run back so examples reflect what the user actually typed.
    descending = [r[::-1] for r in _runs(password[::-1])]
    if ascending or descending:
        examples = (ascending + descending)[:3]
        direction = []
        if ascending:
            direction.append("ascending")
        if descending:
            direction.append("descending")
        return {
            "type": "sequential_pattern",
            "severity": "medium",
            "title": "Sequential characters detected",
            "description": ("Password contains a predictable "
                            f"{' and '.join(direction)} character sequence."),
            "detail": "Sequential runs such as "
                      + ", ".join(f"'{e}'" for e in examples)
                      + " are easy for attackers to guess.",
        }
    return None


def detect_keyboard_patterns(password: str) -> Optional[dict]:
    """Detect keyboard-row and keyboard-walk patterns (qwerty, asdf, 1qaz...)."""
    s = password.lower()
    hits = []
    for row in KEYBOARD_ROWS:
        # forward runs of 3+ (qwe, wert, asdf...)
        for i in range(len(row) - 2):
            tri = row[i:i + 3]
            if tri in s:
                hits.append(tri)
        # reversed runs only at 4+ (fdsa, trew) to avoid false positives on
        # ordinary English bigrams/trigrams such as 'tre' in "tree".
        for i in range(len(row) - 3):
            seg = row[i:i + 4][::-1]
            if seg in s:
                hits.append(seg)
    for walk in KEYBOARD_WALKS:
        if walk in s:
            hits.append(walk)
        if walk[::-1] in s:
            hits.append(walk[::-1])
    if hits:
        hits = sorted(set(hits), key=len, reverse=True)
        return {
            "type": "keyboard_pattern",
            "severity": "medium",
            "title": "Keyboard pattern detected",
            "description": "Password contains a common keyboard pattern.",
            "detail": ("Keyboard walks such as "
                       + ", ".join(f"'{h}'" for h in hits[:3])
                       + " are among the first patterns attackers try."),
        }
    return None


def detect_repetition(password: str) -> list[dict]:
    """Detect repeated characters (aaaa) and repeated substrings (abcabc)."""
    findings = []
    match = re.search(r"(.)\1{2,}", password)
    if match:
        findings.append({
            "type": "repeated_characters",
            "severity": "high",
            "title": "Repeated characters detected",
            "description": "Password repeats the same character several times.",
            "detail": f"The run '{match.group(0)}' is highly predictable.",
        })
    sub = re.search(r"(.{2,12})\1{1,}", password)
    if sub:
        findings.append({
            "type": "repeated_substring",
            "severity": "medium",
            "title": "Repeated substring detected",
            "description": "Password repeats a multi-character pattern.",
            "detail": f"The chunk '{sub.group(1)}' is repeated, which reduces "
                      "unpredictability.",
        })
    return findings


def detect_year_or_date(password: str) -> Optional[dict]:
    """Detect year-like (1900-2099) and date-like patterns."""
    year = re.search(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)", password)
    date = re.search(r"(19|20)\d{2}[-/ ]?(0[1-9]|1[0-2])[-/ ]?(0[1-9]|[12]\d|3[01])",
                     password)
    if year or date:
        hint = (date.group(0) if date else year.group(1))
        return {
            "type": "year_date_pattern",
            "severity": "medium",
            "title": "Year or date-like pattern detected",
            "description": "Password contains a year or date-like pattern.",
            "detail": (f"'{hint}' looks like a year/date. Birth years and "
                       "memorable dates are frequently targeted."),
        }
    return None


def detect_digit_run(password: str) -> Optional[dict]:
    """Detect long purely-numeric runs (phone/PIN-like)."""
    m = re.search(r"\d{4,}", password)
    if m:
        return {
            "type": "numeric_run",
            "severity": "low",
            "title": "Long numeric run detected",
            "description": "Password contains a long run of digits.",
            "detail": f"The digit run '{m.group(0)}' resembles a PIN, phone "
                      "or date fragment.",
        }
    return None


def detect_predictable_structure(password: str, dictionary_words: set[str],
                                 common_passwords: set[str]) -> Optional[dict]:
    """Detect 'common word + digits/symbols' structure (welcome123, admin2026).

    Adding a predictable number to a common word does not create a strong
    password — this structure is exactly what rule-based crackers target.
    """
    match = re.match(r"^([A-Za-z]+)([\d!@#$%^&*+\-_=]*)$", password)
    if not match:
        return None
    word = match.group(1).lower()
    tail = match.group(2)
    if len(word) < 4 or not tail:
        return None
    if word in dictionary_words or word in common_passwords:
        has_year = bool(re.fullmatch(r"(19|20)\d{2}[!@#$%^&*+\-_=]*", tail))
        kind = "word_year_combo" if has_year else "word_number_combo"
        title = ("Predictable word + year pattern"
                 if has_year else "Predictable word + number pattern")
        return {
            "type": "predictable_structure",
            "subtype": kind,
            "severity": "high",
            "title": title,
            "description": "Password is a common word followed by predictable "
                           "characters.",
            "detail": ("A common word plus digits/symbols (word + number"
                       + ("/year" if has_year else "")
                       + ") is one of the most predictable password shapes."),
            "matched_word_length": len(word),
        }
    return None


def run_pattern_checks(password: str, dictionary_words: set[str],
                       common_passwords: set[str]) -> list[dict]:
    """Run every pattern check and return the combined findings list."""
    findings: list[dict] = []
    for result in (detect_sequences(password), detect_keyboard_patterns(password),
                   detect_year_or_date(password), detect_digit_run(password),
                   detect_predictable_structure(password, dictionary_words,
                                                common_passwords)):
        if result:
            findings.append(result)
    findings.extend(detect_repetition(password))
    return findings
