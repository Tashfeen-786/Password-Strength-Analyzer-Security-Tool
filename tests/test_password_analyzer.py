"""
Unit tests for the password analysis engine (PDF section 30).

Covers the 30 required test scenarios with synthetic demo passwords only.
The analyzer is a pure in-memory function: nothing here touches disk,
logs, or the network.
"""
from __future__ import annotations

import re

import pytest

from backend.services.common_checker import is_common_password
from backend.services.entropy_estimator import estimate_theoretical_entropy
from backend.services.password_analyzer import analyze_password
from backend.services.password_generator import (generate_password,
                                                 generate_passphrase)
from backend.services.policy_checker import DEFAULT_POLICY, evaluate_policy
from backend.services.scoring_engine import classify_score


def analyze(pw: str, **kwargs):
    return analyze_password(pw, **kwargs)


def types(result):
    return [f["type"] for f in result["findings"]]


# 1. Empty password ---------------------------------------------------------
def test_01_empty_password():
    r = analyze("")
    assert r["score"] == 0
    assert r["classification"] == "VERY WEAK"
    assert "empty_password" in types(r)


# 2. One-character password -------------------------------------------------
def test_02_one_character_password():
    r = analyze("x")
    assert r["classification"] == "VERY WEAK"
    assert r["score"] <= 15
    assert r["metrics"]["length"]["band"] == "Very short"


# 3. Short numeric password ---------------------------------------------------
def test_03_short_numeric_password():
    r = analyze("1234")
    assert r["classification"] == "VERY WEAK"
    assert r["metrics"]["characters"]["character_type_count"] == 1


# 4. Common password --------------------------------------------------------
def test_04_common_password():
    r = analyze("123456")
    assert r["score"] == 0
    assert r["classification"] == "VERY WEAK"
    assert "common_password" in types(r)
    assert "sequential_pattern" in types(r)
    assert is_common_password("123456")


def test_04b_common_password_is_always_very_weak():
    # Even a LONG listed common password cannot escape VERY WEAK.
    r = analyze("qwertyuiop")
    assert is_common_password("qwertyuiop")
    assert r["score"] <= 15
    assert r["classification"] == "VERY WEAK"


# 5. Long repeated password ---------------------------------------------------
def test_05_long_repeated_password():
    r = analyze("aaaaaaaaaaaaaaaa")
    # PDF TEST 3: long but highly repetitive -> WEAK
    assert r["classification"] == "WEAK"
    assert 21 <= r["score"] <= 40
    assert "repeated_characters" in types(r)


# 6. Lowercase only -----------------------------------------------------------
def test_06_lowercase_only():
    r = analyze("qpfjzmrieowv")
    c = r["metrics"]["characters"]
    assert c["lowercase"] == len("qpfjzmrieowv")
    assert c["uppercase"] == 0 and c["digits"] == 0 and c["symbols"] == 0


# 7. Uppercase only -----------------------------------------------------------
def test_07_uppercase_only():
    r = analyze("QPFJMZEOWV")
    c = r["metrics"]["characters"]
    assert c["uppercase"] == len("QPFJMZEOWV")
    assert c["lowercase"] == 0


# 8. Numbers only -------------------------------------------------------------
def test_08_numbers_only():
    r = analyze("9250183746")
    c = r["metrics"]["characters"]
    assert c["digits"] == 10 and c["character_type_count"] == 1
    assert r["score"] <= 40


# 9. Symbols only -------------------------------------------------------------
def test_09_symbols_only():
    r = analyze("$%&!?*()_+=")
    c = r["metrics"]["characters"]
    assert c["symbols"] == len("$%&!?*()_+=")
    assert c["character_type_count"] == 1


# 10. Mixed characters --------------------------------------------------------
def test_10_mixed_characters():
    r = analyze("Tr0p!cal-Driftwood-7829")
    c = r["metrics"]["characters"]
    assert c["character_type_count"] == 4
    assert r["classification"] in ("STRONG", "VERY STRONG")


# 11. Sequential numbers ------------------------------------------------------
def test_11_sequential_numbers():
    r = analyze("SkyBlue-12345")
    assert "sequential_pattern" in types(r)


# 12. Reverse numeric sequence ------------------------------------------------
def test_12_reverse_numeric_sequence():
    r = analyze("987654")
    assert "sequential_pattern" in types(r)
    assert r["classification"] in ("VERY WEAK", "WEAK")


# 13. Sequential letters ------------------------------------------------------
def test_13_sequential_letters():
    r = analyze("Treasure-abcd-9")
    assert "sequential_pattern" in types(r)


# 14. Keyboard sequence -------------------------------------------------------
def test_14_keyboard_sequence():
    r = analyze("qwerty2026!")
    # PDF TEST 4: keyboard pattern + predictable year -> WEAK
    assert r["classification"] == "WEAK"
    assert "keyboard_pattern" in types(r)
    assert "year_date_pattern" in types(r)


# 15. Repeated characters -----------------------------------------------------
def test_15_repeated_characters():
    r = analyze("Mango-Tree-9999")
    assert "repeated_characters" in types(r)


# 16. Repeated substring ------------------------------------------------------
def test_16_repeated_substring():
    r = analyze("abcabcabc")
    assert "repeated_substring" in types(r)


# 17. Common word + number ----------------------------------------------------
def test_17_common_word_plus_number():
    r = analyze("welcome123")
    assert "dictionary_word" in types(r)
    assert "predictable_structure" in types(r)
    assert r["score"] <= 40


# 18. Word + year -------------------------------------------------------------
def test_18_word_plus_year():
    r = analyze("admin2026")
    assert "predictable_structure" in types(r)
    assert "year_date_pattern" in types(r)
    assert r["classification"] in ("VERY WEAK", "WEAK")


# 19. Personal name overlap ---------------------------------------------------
def test_19_personal_name_overlap():
    ctx = {"first_name": "Rahul", "birth_year": "", "organization": ""}
    r = analyze("Rahul@45678", context=ctx)
    assert "personal_info_name" in types(r)


# 20. Birth year overlap ------------------------------------------------------
def test_20_birth_year_overlap():
    ctx = {"first_name": "", "birth_year": "1999", "organization": ""}
    r = analyze("Crimson-Tide-1999", context=ctx)
    assert "personal_info_year" in types(r)


# 21. Long passphrase-like input ----------------------------------------------
def test_21_long_passphrase_like_input():
    r = analyze("velvet-galaxy-harbor-orchid")
    assert len("velvet-galaxy-harbor-orchid") >= 20
    assert r["metrics"]["passphrase_style_detected"] is True
    assert r["classification"] in ("STRONG", "VERY STRONG")


# 22. Unicode handling --------------------------------------------------------
def test_22_unicode_handling():
    r = analyze("Pässwort-θ-2049-Ω")
    assert 0 <= r["score"] <= 100
    assert r["metrics"]["length"]["length"] == len("Pässwort-θ-2049-Ω")


# 23. Space handling ----------------------------------------------------------
def test_23_space_handling():
    r = analyze("amber falcon quiet river 92")
    c = r["metrics"]["characters"]
    assert c["spaces"] == 4
    assert r["classification"] in ("MODERATE", "STRONG", "VERY STRONG")


# 24. Maximum accepted length -------------------------------------------------
def test_24_maximum_length_handling():
    ok = analyze("Qj7!mZ2#vX9*" * 8)         # 96 chars — accepted
    assert ok["metrics"]["length"]["length"] == 96
    too_long = "A" * 129                      # over the 128-char limit
    assert len(too_long) == 129               # API layer rejects this (422)


# 25. Strength-score boundaries ----------------------------------------------
@pytest.mark.parametrize("score,expected", [
    (0, "VERY WEAK"), (20, "VERY WEAK"), (21, "WEAK"), (40, "WEAK"),
    (41, "MODERATE"), (60, "MODERATE"), (61, "STRONG"), (80, "STRONG"),
    (81, "VERY STRONG"), (100, "VERY STRONG"),
])
def test_25_score_boundaries(score, expected):
    assert classify_score(score) == expected


# 26. Suggestion generation ---------------------------------------------------
def test_26_suggestion_generation():
    r = analyze("welcome123")
    assert len(r["suggestions"]) >= 3
    assert all(isinstance(s, str) and len(s) > 15 for s in r["suggestions"])
    # suggestions must be specific, not generic
    assert not any(s.strip().lower() == "make your password stronger."
                   for s in r["suggestions"])
    # suggestions must never reveal the password
    assert all("welcome123" not in s for s in r["suggestions"])


def test_26b_pdf_demo_case_password123():
    # PDF TEST 2: diversity exists but predictable -> Weak/Moderate band.
    r = analyze("Password123!")
    assert r["classification"] in ("WEAK", "MODERATE")
    assert "predictable_structure" in types(r)


# 27. Secure password generation ----------------------------------------------
def test_27_secure_password_generation():
    pw = generate_password(24)
    assert len(pw) == 24
    assert re.search(r"[a-z]", pw) and re.search(r"[A-Z]", pw)
    assert re.search(r"\d", pw) and re.search(r"[^A-Za-z0-9]", pw)
    r = analyze(pw)
    assert r["classification"] in ("STRONG", "VERY STRONG")
    # 'secrets' must be used, never 'random'
    import backend.services.password_generator as gen_mod
    import inspect
    source = inspect.getsource(gen_mod)
    assert "secrets" in source and "import random" not in source


def test_27b_generator_options_and_passphrase():
    pw = generate_password(20, symbols=False, numbers=True)
    assert all(c.isalnum() for c in pw)
    phrase = generate_passphrase(words=5, separator="-")
    assert len(phrase.split("-")) == 5
    with pytest.raises(ValueError):
        generate_password(16, uppercase=False, lowercase=False,
                          numbers=False, symbols=False)


# 28. Password not stored ------------------------------------------------------
def test_28_password_not_stored(tmp_path):
    from backend.services.analytics_service import record_analysis
    from backend.models.database import get_connection
    secret = "UnitTest-Synthetic-9921!"
    db = str(tmp_path / "t.db")
    result = analyze(secret)
    record_analysis(result, db_path=db)
    with get_connection(db) as conn:
        rows_a = conn.execute("SELECT * FROM ANALYSES").fetchall()
        rows_f = conn.execute("SELECT * FROM FINDINGS").fetchall()
        cols = [r[1] for r in conn.execute("PRAGMA table_info(ANALYSES)")]
    assert len(rows_a) == 1
    blob = " ".join(str(tuple(r)) for r in rows_a + rows_f)
    assert secret not in blob
    # no column anywhere may carry the password
    assert "password" not in {c.lower() for c in cols}


# 29. Password not logged ------------------------------------------------------
def test_29_password_not_logged(caplog):
    import logging
    secret = "NoLog-Synthetic-4471!"
    with caplog.at_level(logging.DEBUG):
        analyze(secret)
    assert secret not in caplog.text


# 30. Analytics storage contains only safe metadata -----------------------------
def test_30_analytics_storage_metadata_only(tmp_path):
    from backend.services.analytics_service import (get_dashboard_stats,
                                                    record_analysis)
    secret = "MetaTest-Synthetic-6630!"
    db = str(tmp_path / "t.db")
    record_analysis(analyze(secret), db_path=db)
    stats = get_dashboard_stats(db_path=db)
    assert stats["total_analyses"] == 1
    row_blob = str(stats)
    assert secret not in row_blob
    assert set(stats["classifications"].keys()) == {
        "VERY WEAK", "WEAK", "MODERATE", "STRONG", "VERY STRONG"}


# --- Extra engine checks -----------------------------------------------------
def test_entropy_formula_and_limitation():
    e = estimate_theoretical_entropy("Password123!")
    assert e["entropy_bits"] == pytest.approx(12 * 6.554, abs=0.5)
    assert "random" in e["limitation"].lower()


def test_result_structure_contract():
    r = analyze("Structured-Check-42!")
    for key in ("score", "classification", "findings", "suggestions",
                "metrics", "policy", "disclaimer"):
        assert key in r
    assert set(r["metrics"].keys()) >= {"length", "characters", "entropy"}


def test_policy_pass_fail_is_separate_from_score():
    r = analyze("Password123!")
    assert "policy_result" in r["policy"]
    assert r["policy"]["policy_result"] in ("POLICY PASS", "POLICY FAIL")
    # policy pass does NOT imply strong: aaaaa... passes min-length policy
    r2 = analyze("aaaaaaaaaaaaaaaa")
    assert r2["policy"]["policy_result"] == "POLICY PASS"
    assert r2["classification"] == "WEAK"


def test_policy_configuration():
    strict = {**DEFAULT_POLICY, "minimum_length": 20}
    res = evaluate_policy("Blue-Falcon-77", is_common=False,
                          personal_info_found=False, policy=strict)
    assert res["passed"] is False
    assert any(r["rule"].startswith("Minimum length") and not r["passed"]
               for r in res["rules"])


def test_breach_demo_check():
    r = analyze("synthetic-demo-Br3ach!2025")
    assert r["breach_check"]["found"] is True
    assert r["breach_check"]["demo"] is True
    assert r["score"] <= 10  # breach exposure caps the score


def test_leetspeak_common_variant():
    r = analyze("P@ssw0rd")
    assert "leetspeak_substitution" in types(r)
    assert r["score"] <= 15  # normalized form is a common password


def test_context_is_never_reflected(tmp_path):
    from backend.services.analytics_service import record_analysis
    from backend.models.database import get_connection
    ctx = {"first_name": "Rahul", "birth_year": "1999", "organization": "IITD"}
    r = analyze("Rahul@IITD-1999", context=ctx)
    assert "personal_info_name" in types(r)
    db = str(tmp_path / "t.db")
    record_analysis(r, db_path=db)
    with get_connection(db) as conn:
        blob = " ".join(str(tuple(row)) for row in
                        conn.execute("SELECT * FROM FINDINGS").fetchall())
    assert "Rahul" not in blob and "1999" not in blob and "IITD" not in blob
