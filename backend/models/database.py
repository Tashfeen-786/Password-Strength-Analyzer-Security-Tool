"""
SQLite persistence for PRIVACY-SAFE aggregate analytics (PDF sections 20-22).

Schema (PDF section 22) — deliberately contains NO password column:

    ANALYSES(
        analysis_id            INTEGER PRIMARY KEY AUTOINCREMENT,
        score                  INTEGER NOT NULL,
        classification         TEXT    NOT NULL,
        password_length        INTEGER NOT NULL,
        unique_character_ratio REAL    NOT NULL,
        weakness_count         INTEGER NOT NULL,
        created_at             TEXT    NOT NULL
    )

    FINDINGS(
        finding_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id  INTEGER NOT NULL REFERENCES ANALYSES(analysis_id),
        finding_type TEXT    NOT NULL,
        severity     TEXT    NOT NULL,
        description  TEXT    NOT NULL
    )

WHY NO PASSWORD COLUMN (and not even a password-hash column):
Storing plaintext passwords would instantly turn this educational tool into
a credential database — a breach of our own database would expose users.
A reversible (encrypted) password column would have the same practical
effect for anyone obtaining the key. Even storing *hashes* of arbitrary
user-submitted passwords is an unnecessary risk here: the analyzer does not
need to verify users later, and a low-entropy submitted password could be
recovered by an offline guessing attack against the hash. Therefore only
non-secret, aggregate metadata is persisted.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing

from ..utils.config import DB_PATH

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ANALYSES (
    analysis_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    score                  INTEGER NOT NULL,
    classification         TEXT    NOT NULL,
    password_length        INTEGER NOT NULL,
    unique_character_ratio REAL    NOT NULL,
    weakness_count         INTEGER NOT NULL,
    created_at             TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS FINDINGS (
    finding_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id  INTEGER NOT NULL REFERENCES ANALYSES(analysis_id),
    finding_type TEXT    NOT NULL,
    severity     TEXT    NOT NULL,
    description  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_analyses_class ON ANALYSES(classification);
CREATE INDEX IF NOT EXISTS idx_findings_type ON FINDINGS(finding_type);
"""

# Every column that exists in the database, for privacy auditing.
SAFE_COLUMNS = {
    "ANALYSES": {"analysis_id", "score", "classification", "password_length",
                 "unique_character_ratio", "weakness_count", "created_at"},
    "FINDINGS": {"finding_id", "analysis_id", "finding_type", "severity",
                 "description"},
}


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | None = None) -> None:
    """Create the analytics schema if it does not exist."""
    with closing(get_connection(db_path)) as conn, conn:
        conn.executescript(SCHEMA_SQL)


def get_schema_ddl(db_path: str | None = None) -> str:
    """Return the live schema DDL — used as database evidence of the
    'no password field' privacy property."""
    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type IN ('table','index') "
            "AND sql IS NOT NULL ORDER BY name").fetchall()
    return ";\n\n".join(row[0] for row in rows) + ";"
