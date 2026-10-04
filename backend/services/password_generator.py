"""
Secure password generator (PDF section 19) — DEFENSIVE feature.

Uses Python's `secrets` module (cryptographically secure randomness),
NOT `random`. `random` is a deterministic PRNG designed for simulation,
not security; `secrets` draws from the OS CSPRNG and is the documented,
recommended source for security-sensitive randomness.

Generated passwords are returned once to the caller and NEVER stored.
They are demonstration output and should not be reused verbatim.
"""
from __future__ import annotations

import secrets
import string

SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?"
# Demo passphrase word pool (all present in data/dictionary_words.txt — the
# point, taught in the UI, is that passphrase strength comes from the NUMBER
# and RANDOMNESS of words, not from word obscurity).
PASSPHRASE_WORDS = [
    "river", "candle", "photon", "saffron", "galaxy", "orchid", "drift",
    "ember", "velvet", "harbor", "turtle", "prairie", "harvest", "crystal",
    "phoenix", "panda", "planet", "rocket", "silver", "thunder", "winter",
    "solar", "lunar", "cobalt",
]


def generate_password(length: int = 16, *, uppercase: bool = True,
                      lowercase: bool = True, numbers: bool = True,
                      symbols: bool = True) -> str:
    """Generate a cryptographically secure random password.

    Length is clamped to [8, 64]. At least one character class must be on.
    Guarantees at least one character from every enabled class.
    """
    length = max(8, min(64, int(length)))
    pools: list[str] = []
    if lowercase:
        pools.append(string.ascii_lowercase)
    if uppercase:
        pools.append(string.ascii_uppercase)
    if numbers:
        pools.append(string.digits)
    if symbols:
        pools.append(SYMBOLS)
    if not pools:
        raise ValueError("At least one character class must be enabled.")

    alphabet = "".join(pools)
    # Guarantee representation of each enabled class...
    chars = [secrets.choice(pool) for pool in pools]
    # ...then fill the rest from the full alphabet and shuffle securely.
    chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def generate_passphrase(words: int = 4, separator: str = "-") -> str:
    """Generate a random multi-word demo passphrase (dictionary teaching aid)."""
    words = max(3, min(8, int(words)))
    separator = separator if separator in ("-", "_", ".", " ") else "-"
    return separator.join(secrets.choice(PASSPHRASE_WORDS)
                          for _ in range(words))
