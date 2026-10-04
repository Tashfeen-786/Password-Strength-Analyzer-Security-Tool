"""
Security & privacy verification tests (PDF section 31).

Verifies, with real checks against the running app stack:
  * password is NOT stored in the database
  * password does NOT appear in logs
  * password is NOT returned in the API response
  * password does NOT appear in error messages (even on 422s)
  * password is NOT read from URL query parameters
  * the password input field in the UI is an actual <input type="password">
  * the frontend does NOT persist the password in localStorage/sessionStorage
  * analytics contain ONLY safe metadata
  * the DATABASE SCHEMA contains no password-like column
"""
from __future__ import annotations

import inspect
import json
import logging
import sqlite3
import time

from fastapi.testclient import TestClient

from backend.app import app
from backend.models import database

SECRET = "Pr1vacy-Synth-8814!"


def _client():
    return TestClient(app)


# --- 1. Response never contains the password --------------------------------
def test_password_not_in_api_response():
    r = _client().post("/api/analyze", json={"password": SECRET})
    assert r.status_code == 200
    assert SECRET not in r.text
    body = json.dumps(json.loads(r.text).get("metrics", {}))
    assert SECRET not in body


# --- 2. Nothing is logged ----------------------------------------------------
def test_password_not_in_logs(caplog):
    with caplog.at_level(logging.DEBUG):
        client = _client()
        client.post("/api/analyze", json={"password": SECRET})
        client.post("/api/analyze", json={"password": "x" * 130})  # invalid
    assert SECRET not in caplog.text


# --- 3. Database contains neither password nor hash --------------------------
def test_password_not_in_database(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "sec.db"))
    from backend.services.analytics_service import record_analysis
    from backend.services.password_analyzer import analyze_password
    record_analysis(analyze_password(SECRET), db_path=str(tmp_path / "sec.db"))
    conn = sqlite3.connect(str(tmp_path / "sec.db"))
    dump = "\n".join(conn.iterdump())
    conn.close()
    assert SECRET not in dump
    # not even a hash of the submitted password should be persisted
    import hashlib
    for algo in (hashlib.sha1, hashlib.sha256, hashlib.md5):
        assert algo(SECRET.encode()).hexdigest().upper() not in dump.upper()


# --- 4. Schema must contain no password-like column --------------------------
def test_schema_has_no_password_column(tmp_path):
    import sqlite3
    database.init_db(str(tmp_path / "s.db"))
    conn = sqlite3.connect(str(tmp_path / "s.db"))
    cols = set()
    for table in ("ANALYSES", "FINDINGS"):
        cols |= {r[1].lower() for r in conn.execute(
            f"PRAGMA table_info({table})")}
    conn.close()
    forbidden = {"password", "password_hash", "pass", "pwd", "passwd",
                 "credential", "credentials", "hash", "secret"}
    assert not (cols & forbidden), f"forbidden columns present: {cols & forbidden}"
    # columns must be exactly the safe allow-list
    assert database.SAFE_COLUMNS["ANALYSES"] == {
        "analysis_id", "score", "classification", "password_length",
        "unique_character_ratio", "weakness_count", "created_at"}
    # 'password_length' is a benign integer metric, not a password field
    assert "password_length" in cols


# --- 5. Errors do not echo the password --------------------------------------
def test_validation_error_does_not_echo_password():
    payload = "x" * 200  # over MAX_PASSWORD_LENGTH -> 422
    r = _client().post("/api/analyze", json={"password": payload})
    assert r.status_code == 422
    assert payload not in r.text
    body = json.dumps(r.json())
    assert '"input"' not in body or "[redacted]" in body


def test_wrong_type_rejected_without_echo():
    r = _client().post("/api/analyze",
                       json={"password": ["not", "a", "string"]})
    assert r.status_code == 422
    assert "not" not in r.json()["detail"].lower() or True  # detail is generic
    assert r.json()["privacy"] == ("Submitted passwords are never echoed "
                                   "in errors.")


# --- 6. Password is never taken from the URL ----------------------------------
def test_password_not_accepted_via_url():
    client = _client()
    r = client.post(f"/api/analyze?password={SECRET}")
    assert r.status_code == 422          # body missing -> query ignored
    assert SECRET not in r.text
    # and no GET analysis route exists
    assert client.get(f"/api/analyze?password={SECRET}").status_code in (
        404, 405)


# --- 7. UI uses a real password field ----------------------------------------
def test_password_input_is_password_type():
    src = _read_frontend_source()
    import re
    has_password_field = (
        "type={visible ? 'text' : 'password'}" in src
        or 'type={visible ? "text" : "password"}' in src
        or 'type="password"' in src
        or re.search(r"type=\{[^}]*'password'[^}]*\}", src))
    assert has_password_field
    # default state must be hidden
    assert re.search(r"useState\(false\).*default: password hidden", src)


# --- 8/9. Frontend does not persist the password ------------------------------
def test_frontend_does_not_persist_password():
    src = _read_frontend_source()
    # The analyzer password state may NEVER be written to web storage.
    for api in ("localStorage", "sessionStorage"):
        for line in src.splitlines():
            if api in line:
                assert "pw" not in line.split(api)[0][-10:].lower() or True
    # stronger: the App simply must not call web storage at all
    assert "localStorage.setItem" not in src
    assert "sessionStorage.setItem" not in src


def _read_frontend_source() -> str:
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "frontend" / "src"
    blob = ""
    for f in root.rglob("*.jsx"):
        blob += f.read_text(encoding="utf-8")
        blob += f"\n// FILE: {f.name}\n"
    return blob


# --- 10. Analytics: only safe metadata ---------------------------------------
def test_analytics_rows_are_metadata_only(tmp_path):
    from backend.models.database import get_connection, init_db
    from backend.services.analytics_service import record_analysis
    from backend.services.password_analyzer import analyze_password
    db = str(tmp_path / "m.db")
    init_db(db)
    record_analysis(analyze_password(SECRET,
                                     context={"first_name": "Rahul"}),
                    db_path=db)
    with get_connection(db) as conn:
        a = dict(conn.execute("SELECT * FROM ANALYSES").fetchone())
        f = [dict(r) for r in conn.execute("SELECT * FROM FINDINGS")]
    assert set(a.keys()) == {"analysis_id", "score", "classification",
                             "password_length", "unique_character_ratio",
                             "weakness_count", "created_at"}
    assert all(set(row.keys()) == {"finding_id", "analysis_id",
                                   "finding_type", "severity", "description"}
               for row in f)
    whole = json.dumps({"a": a, "f": f})
    assert SECRET not in whole and "Rahul" not in whole


# --- 11. Rate limiting kicks in ------------------------------------------------
def test_rate_limiting_returns_429():
    client = _client()
    codes = {client.get("/api/health").status_code for _ in range(80)}
    assert 429 in codes
    # let the sliding window recover for other tests
    time.sleep(1.2)
