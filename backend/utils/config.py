"""
Central configuration for the Password Strength Analyzer backend.

Values can be overridden with environment variables (see .env.example).
Absolutely no secret values are required to run this project.
"""
from __future__ import annotations

import os
from pathlib import Path

# --- Paths ----------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = os.getenv("PSA_DB_PATH", str(PROJECT_ROOT / "backend" / "analytics.db"))

# --- Analyzer limits -------------------------------------------------------
# Maximum accepted password length (PDF section 34: "Maximum supported length: 128+")
MAX_PASSWORD_LENGTH = int(os.getenv("PSA_MAX_PASSWORD_LENGTH", "128"))

# --- Data files ------------------------------------------------------------
COMMON_PASSWORDS_FILE = os.getenv(
    "PSA_COMMON_PASSWORDS", str(DATA_DIR / "common_passwords.txt")
)
DICTIONARY_WORDS_FILE = os.getenv(
    "PSA_DICTIONARY_WORDS", str(DATA_DIR / "dictionary_words.txt")
)
BREACH_HASHES_FILE = os.getenv(
    "PSA_BREACH_HASHES", str(DATA_DIR / "breached_sha1.txt")
)

# --- Analytics -------------------------------------------------------------
# Privacy-safe aggregate analytics are ON by default but can be disabled.
ENABLE_ANALYTICS = os.getenv("PSA_ENABLE_ANALYTICS", "true").lower() == "true"

# --- Rate limiting (demo-grade, in-memory) ---------------------------------
RATE_LIMIT_REQUESTS = int(os.getenv("PSA_RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("PSA_RATE_LIMIT_WINDOW_SECONDS", "60"))
