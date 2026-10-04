"""
Standalone EDUCATIONAL password-hashing demonstration (PDF section 32).

    Password -> Salt -> PBKDF2-HMAC-SHA256 (600k iterations) -> Stored Hash

Uses a SYNTHETIC demo password only. This demo is deliberately separate from
the analyzer: analyzer input is never persisted into any password store.

Run:  python scripts/hashing_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.hashing_demo import hash_password, verify_password

DEMO_PASSWORD = "synthetic-demo-Only!2025"   # clearly synthetic


def main() -> None:
    print("=" * 72)
    print(" PASSWORD HASHING DEMONSTRATION (educational, synthetic password)")
    print("=" * 72)
    print(f"\nDemo password (synthetic): {DEMO_PASSWORD}")
    print("\nConcept:  Password -> Salt -> PBKDF2-HMAC-SHA256 -> Stored Hash")

    stored_1 = hash_password(DEMO_PASSWORD)
    stored_2 = hash_password(DEMO_PASSWORD)

    print(f"\nStored hash #1: {stored_1}")
    print(f"\nStored hash #2: {stored_2}")
    print("\nNotice: SAME password, DIFFERENT stored values — each hash uses a")
    print("unique random salt, defeating precomputed rainbow-table lookups.")

    ok = verify_password(DEMO_PASSWORD, stored_1)
    bad = verify_password("WrongDemo-Password", stored_1)
    print(f"\nverify(correct password)  -> {ok}")
    print(f"verify(incorrect password)-> {bad}")

    print("\nKey points:")
    print("  * Hashing is ONE-WAY verification — the original password is never")
    print("    recovered from the stored value.")
    print("  * Hashing is NOT encryption (encryption is reversible with a key).")
    print("  * Fast general-purpose hashes (MD5/SHA-1/SHA-256 alone) are NOT")
    print("    suitable for password storage. Use Argon2id, bcrypt, scrypt or")
    print("    PBKDF2 with an appropriate work factor.")
    print("  * This project never stores analyzer passwords at all — this demo is")
    print("    purely educational.")


if __name__ == "__main__":
    main()
