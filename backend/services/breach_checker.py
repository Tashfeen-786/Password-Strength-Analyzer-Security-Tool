"""
Local demo breach-exposure check (k-anonymity concept, PDF Step 4).

PRIVACY DESIGN:
  * The password is hashed locally (SHA-1, upper-case hex) and compared
    against a tiny SYNTHETIC demo corpus stored in data/breached_sha1.txt.
  * The plaintext password never leaves the backend and is never logged or
    stored; only the in-memory hash comparison happens.
  * No external breach service is contacted by default.

PRODUCTION NOTE: real deployments use a k-anonymity scheme in which only the
first 5 hex characters of a hash are sent to an API, so the service never
learns the password. This project demonstrates the concept fully locally,
educationally, with invented demo data.

The demo corpus contains SHA-1 hashes of clearly synthetic strings such as
'synthetic-demo-Br3ach!2025' plus a few of this project's classroom demo
passwords (e.g. 'qwerty2026!'). It is intentionally tiny.
"""
from __future__ import annotations

import hashlib

from ..utils.config import BREACH_HASHES_FILE


def load_breach_hashes(path: str = BREACH_HASHES_FILE) -> set[str]:
    """Load the local synthetic breach-hash demo set into memory."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return {line.strip().upper() for line in fh if line.strip()}
    except OSError:
        return set()


BREACH_HASHES: set[str] = load_breach_hashes()


def check_breach_exposure(password: str,
                          hashes: set[str] | None = None) -> dict:
    """Educational demo breach check.

    Returns {checked, found, corpus_size, demo, note}. ``found`` means the
    password appeared in the synthetic demo corpus.
    """
    hashes = hashes if hashes is not None else BREACH_HASHES
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    found = digest in hashes
    return {
        "checked": True,
        "found": found,
        "corpus_size": len(hashes),
        "demo": True,
        "note": (
            "EDUCATIONAL DEMO ONLY: compared against a tiny local set of "
            "synthetic hashes. No password was sent to any external service. "
            "Production systems should use a k-anonymity breach-check API."
        ),
    }


def breach_finding() -> dict:
    return {
        "type": "breach_exposure",
        "severity": "critical",
        "title": "Found in demo breach list",
        "description": "Password appears in the (synthetic demo) breach corpus.",
        "detail": ("This password was found in the local demo breach list. "
                   "Never use a password that has appeared in a breach."),
    }
