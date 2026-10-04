"""
SEPARATE educational password-hashing demonstration (PDF section 32).

    Password -> Salt -> Password-Hashing Function -> Stored Hash

Demonstrates safe password-storage *concepts* using PBKDF2-HMAC-SHA256 from
the Python standard library (no third-party dependency required):

  * hash_password(password)   -> "pbkdf2$iterations$salt_hex$hash_hex"
  * verify_password(password, stored) -> bool

IMPORTANT BOUNDARIES (enforced by design of the whole project):
  * This module is educational and standalone. It is NOT wired into the
    analyzer; analyzer input is never persisted into password storage.
  * Hashing is ONE-WAY verification. Hashing is not encryption: encryption
    is reversible with a key; a password hash is not meant to be reverted.
  * General-purpose fast hashes (MD5/SHA-1/SHA-256 alone) are NOT suitable
    for password storage. Use dedicated password-hashing / key-stretching
    functions: Argon2id (preferred), bcrypt, scrypt, or PBKDF2 with an
    appropriate work factor.

Only synthetic demo passwords must be used with this demonstration.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000  # current OWASP-style recommended work factor
SALT_BYTES = 16
DKLEN = 32


def hash_password(password: str, *, salt: bytes | None = None,
                  iterations: int = ITERATIONS) -> str:
    """Hash a (synthetic demo) password with a unique random salt."""
    if not isinstance(password, str) or password == "":
        raise ValueError("A non-empty demo password string is required.")
    salt = salt if salt is not None else secrets.token_bytes(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                  salt, iterations, DKLEN)
    return f"{ALGORITHM}${iterations}${salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against a stored PBKDF2 string (constant-time)."""
    try:
        algorithm, iter_s, salt_hex, hash_hex = stored.split("$")
        if algorithm != ALGORITHM:
            return False
        derived = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex),
            int(iter_s), DKLEN).hex()
        return hmac.compare_digest(derived, hash_hex)
    except (ValueError, TypeError):
        return False
