"""
Privacy-safe aggregate analytics (PDF sections 20-21).

WHAT WE STORE per analysis (and ONLY this):

    analysis_id, score, classification, password_length,
    unique_character_ratio, weakness_count, created_at
    + findings (finding_type, severity, generic description)

WHAT WE NEVER STORE: the password, a reversible form of it, a hash of it,
the optional personal context, or any substring of the password.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone

from ..models.database import get_connection, init_db
from ..utils.config import ENABLE_ANALYTICS


def record_analysis(result: dict, db_path: str | None = None) -> int | None:
    """Persist safe aggregate metadata for one analysis.

    Accepts the analyzer *result* (derived metrics only). Returns the new
    analysis_id, or None when analytics are disabled.
    """
    if not ENABLE_ANALYTICS:
        return None
    init_db(db_path)
    metrics = result["metrics"]
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    findings = result.get("findings", [])
    with closing(get_connection(db_path)) as conn, conn:
        cur = conn.execute(
            """
            INSERT INTO ANALYSES (score, classification, password_length,
                                  unique_character_ratio, weakness_count,
                                  created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                result["score"],
                result["classification"],
                metrics["length"]["length"],
                metrics["characters"]["unique_character_ratio"],
                len(findings),
                created_at,
            ),
        )
        analysis_id = cur.lastrowid
        conn.executemany(
            """
            INSERT INTO FINDINGS (analysis_id, finding_type, severity,
                                  description)
            VALUES (?, ?, ?, ?)
            """,
            [(analysis_id, f["type"], f["severity"],
              # store ONLY the generic, pattern-free description
              f["description"]) for f in findings],
        )
    return analysis_id


def get_dashboard_stats(db_path: str | None = None) -> dict:
    """Aggregate statistics for the dashboard (PDF section 21)."""
    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        totals = conn.execute(
            "SELECT COUNT(*) AS total, COALESCE(AVG(score),0) AS avg_score "
            "FROM ANALYSES").fetchone()
        class_rows = conn.execute(
            "SELECT classification, COUNT(*) AS n FROM ANALYSES "
            "GROUP BY classification").fetchall()
        length_rows = conn.execute(
            "SELECT password_length AS length, COUNT(*) AS n FROM ANALYSES "
            "GROUP BY password_length ORDER BY length").fetchall()
        score_rows = conn.execute(
            "SELECT score, COUNT(*) AS n FROM ANALYSES "
            "GROUP BY score ORDER BY score").fetchall()

    class_counts = {c: 0 for c in
                    ("VERY WEAK", "WEAK", "MODERATE", "STRONG", "VERY STRONG")}
    for row in class_rows:
        class_counts[row["classification"]] = row["n"]

    # Score histogram in bands of 10.
    histogram = {f"{lo}-{lo + 9 if lo < 100 else 100}": 0
                 for lo in range(0, 100, 10)}
    for row in score_rows:
        lo = min(row["score"] // 10 * 10, 90)
        key = f"{lo}-{lo + 9 if lo < 100 else 100}"
        histogram[key] = histogram.get(key, 0) + row["n"]

    return {
        "total_analyses": totals["total"],
        "average_score": round(totals["avg_score"], 1),
        "classifications": class_counts,
        "length_distribution": [dict(r) for r in length_rows],
        "score_distribution": [{"band": k, "count": v}
                               for k, v in histogram.items()],
        "privacy_note": ("Aggregate metadata only. The database contains no "
                         "passwords, no password hashes, and no personal "
                         "context."),
    }


def get_weakness_analytics(db_path: str | None = None) -> dict:
    """Most common weakness types + pattern detection frequency (charts 3/5)."""
    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        rows = conn.execute(
            "SELECT finding_type, severity, COUNT(*) AS n FROM FINDINGS "
            "GROUP BY finding_type, severity ORDER BY n DESC").fetchall()

    weakness = [
        {"type": r["finding_type"], "severity": r["severity"], "count": r["n"]}
        for r in rows]
    pattern_keys = {"sequential_pattern", "keyboard_pattern",
                    "repeated_characters", "repeated_substring",
                    "predictable_structure", "year_date_pattern",
                    "numeric_run"}
    pattern_frequency = [
        {"type": w["type"], "count": w["count"]}
        for w in weakness if w["type"] in pattern_keys]
    return {
        "weakness_types": weakness,
        "pattern_frequency": pattern_frequency,
        "note": "Finding types/severities only — descriptions stored are "
                "generic and never contain password content.",
    }
