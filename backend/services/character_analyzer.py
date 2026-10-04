"""
Character analysis (PDF section 6).

Detects lowercase, uppercase, digits, symbols and spaces (where permitted),
and computes:

    unique_character_count
    character_type_count
    unique_character_ratio

Character diversity helps, but it must never be the only metric:
``Password123!`` has diversity yet remains highly predictable.
"""
from __future__ import annotations


def analyze_characters(password: str) -> dict:
    lower = sum(1 for c in password if c.islower())
    upper = sum(1 for c in password if c.isupper())
    digit = sum(1 for c in password if c.isdigit())
    space = sum(1 for c in password if c.isspace())
    symbol = sum(1 for c in password if not c.isalnum() and not c.isspace())

    length = len(password)
    unique_count = len(set(password))
    type_count = sum(1 for n in (lower, upper, digit, symbol + space) if n > 0)

    return {
        "length": length,
        "lowercase": lower,
        "uppercase": upper,
        "digits": digit,
        "symbols": symbol,
        "spaces": space,
        "has_lowercase": lower > 0,
        "has_uppercase": upper > 0,
        "has_digits": digit > 0,
        "has_symbols": (symbol + space) > 0,
        "character_type_count": type_count,
        "unique_character_count": unique_count,
        "unique_character_ratio": round(unique_count / length, 3) if length else 0.0,
    }
