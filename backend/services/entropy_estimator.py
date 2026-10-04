"""
Entropy-style estimation (PDF section 13).

    Entropy ~= L * log2(N)

    L = password length
    N = estimated character pool (the size of the alphabet the password
        appears to be drawn from)

IMPORTANT LIMITATION (taught by the project):
This estimate assumes characters were chosen **uniformly at random**.
Human-generated passwords are almost never truly random, so a password like
``Password123!`` can receive an optimistic *theoretical* entropy estimate
while still being highly predictable. That is why this project combines the
entropy estimate with pattern analysis instead of trusting entropy alone.
"""
from __future__ import annotations

import math
import string

LOWER_POOL = 26
UPPER_POOL = 26
DIGIT_POOL = 10
# string.punctuation has 32 chars; +1 for the space character.
SYMBOL_POOL = len(string.punctuation) + 1  # 33


def estimate_pool_size(password: str) -> int:
    """Estimate the character pool N from the character classes present."""
    pool = 0
    if any(c.islower() for c in password):
        pool += LOWER_POOL
    if any(c.isupper() for c in password):
        pool += UPPER_POOL
    if any(c.isdigit() for c in password):
        pool += DIGIT_POOL
    if any((not c.isalnum()) for c in password):  # symbols + whitespace
        pool += SYMBOL_POOL
    return max(pool, 1)


def estimate_theoretical_entropy(password: str) -> dict:
    """Return the theoretical entropy estimate and its inputs.

    Returns a dict so the UI can explain the formula transparently:
    {length, pool_size, entropy_bits, formula, limitation}
    """
    length = len(password)
    pool = estimate_pool_size(password)
    bits = length * math.log2(pool) if length else 0.0
    return {
        "length": length,
        "pool_size": pool,
        "entropy_bits": round(bits, 1),
        "formula": "Entropy ~= L x log2(N)",
        "limitation": (
            "Theoretical estimate only. It assumes random character selection; "
            "human-made passwords are usually far more predictable than this "
            "number suggests."
        ),
    }


def guess_resistance_label(entropy_bits: float) -> str:
    """Educational, deliberately rough guess-resistance label.

    Assumes an *offline* attacker making 10 billion (1e10) guesses per second
    against a **randomly generated** password. Labelled as an educational
    estimate only — real-world resistance depends on the attacker model,
    password predictability, the password-hashing algorithm, its work factor,
    rate limiting, and whether the attack is online or offline.
    """
    if entropy_bits <= 0:
        return "instantly guessable (educational estimate)"
    seconds = 2 ** entropy_bits / 1e10
    if seconds < 1:
        return "under a second (educational estimate)"

    def fmt(value: float, unit: str) -> str:
        irregular = {"century": "centuries"}
        plural = unit if round(value) == 1 else irregular.get(unit, unit + "s")
        return f"about {value:,.0f} {plural} (educational estimate only)"

    bands = [("second", 1), ("minute", 60), ("hour", 3600), ("day", 86400),
             ("year", 31557600), ("century", 31557600 * 100)]
    value, unit, divisor = seconds, "second", 1
    for name, div in bands:
        if seconds >= div:
            unit, divisor = name, div
    value = seconds / divisor
    if unit == "century" and value >= 1000:
        return "millennia upon millennia (educational estimate only)"
    return fmt(value, unit)
