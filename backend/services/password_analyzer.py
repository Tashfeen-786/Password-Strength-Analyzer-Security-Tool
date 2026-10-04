"""
Password analysis orchestrator (PDF section 4).

    analyze_password(password, context=None, policy=None)

Workflow (everything happens transiently, in memory):

    Length Analysis | Character Analysis | Common Password Check |
    Dictionary Check | Sequence Detection | Keyboard Pattern Detection |
    Repetition Detection | Predictable Structure | Context Check |
    Entropy-Style Estimation  -->  Scoring Engine --> Classification
                                  --> Suggestion Engine --> Policy Check

Returns structured output:

    {
      "score": 0, "classification": "",
      "findings": [], "suggestions": [], "metrics": {},
      "policy": {...}, "breach_check": {...}
    }

PRIVACY: the submitted password and the optional context are never stored,
never logged, never returned, and never included in any error message.
"""
from __future__ import annotations

from . import breach_checker, common_checker, context_checker, pattern_detector
from .character_analyzer import analyze_characters
from .entropy_estimator import (estimate_pool_size, estimate_theoretical_entropy,
                                guess_resistance_label)
from .length_analyzer import analyze_length
from .policy_checker import evaluate_policy
from .scoring_engine import compute_score
from .suggestion_engine import generate_suggestions


def _empty_password_result(policy: dict | None) -> dict:
    from .breach_checker import check_breach_exposure
    from .policy_checker import evaluate_policy as _eval_policy
    return {
        "score": 0,
        "classification": "VERY WEAK",
        "findings": [{
            "type": "empty_password",
            "severity": "critical",
            "title": "Empty password",
            "description": "No password was provided.",
            "detail": "An empty password provides no protection at all.",
        }],
        "suggestions": [
            "Use a passphrase of several random words or a generated "
            "password of at least 16 characters.",
            "Use a password manager to generate and store unique passwords.",
            "Enable MFA (multi-factor authentication) wherever it is available.",
        ],
        "metrics": {
            "length": analyze_length(""),
            "characters": analyze_characters(""),
            "entropy": estimate_theoretical_entropy(""),
            "passphrase_style_detected": False,
            "guess_resistance": "instantly guessable (educational estimate)",
            "score_breakdown": {
                "contributions": {}, "penalties": {},
                "total_penalty": 0, "breach_cap_applied": False,
            },
        },
        "breach_check": check_breach_exposure(""),
        "policy": _eval_policy("", is_common=False,
                               personal_info_found=False, policy=policy),
        "disclaimer": _disclaimer(),
    }


def _disclaimer() -> str:
    return ("Strength score and classification are project-defined, "
            "educational estimates — not universal security standards. "
            "Password strength cannot be perfectly determined by one formula.")


def analyze_password(password: str, context: dict | None = None,
                     policy: dict | None = None,
                     breach_hashes: set[str] | None = None) -> dict:
    """Run the complete analysis pipeline and return structured results."""
    password = password or ""
    if len(password) == 0:
        return _empty_password_result(policy)

    # --- derived metrics only (password itself stays transient) ---
    length_info = analyze_length(password)
    char_info = analyze_characters(password)
    entropy_info = estimate_theoretical_entropy(password)
    pool_size = estimate_pool_size(password)

    is_common = common_checker.is_common_password(password)
    dict_words = common_checker.find_dictionary_words(password)

    # Leetspeak pass: 'P@ssw0rd' normalizes to 'password' — run the common /
    # dictionary checks on the normalized form too. Only treated as a hit
    # when normalization reveals a NEW common password or NEW dictionary word
    # (so ordinary 'word + digits' passwords are not mis-flagged).
    leet = common_checker.normalize_leet(password)
    leet_words = set(common_checker.find_dictionary_words(leet))
    original_words = set(dict_words)
    leet_hit = (leet != password.lower() and (
        (common_checker.is_common_password(leet) and not is_common)
        or bool(leet_words - original_words)))
    if leet_hit:
        is_common = is_common or common_checker.is_common_password(leet)
        dict_words = sorted(original_words | leet_words)
    dictionary_hit = bool(dict_words)

    # Passphrase-style mitigation: a LONG password built from 3+ separated
    # dictionary words is a deliberately constructed passphrase (PDF section
    # 18 encourages passphrases). The dictionary weakness is reduced because
    # the strength comes from word count and length, not word obscurity.
    passphrase_style = (len(password) >= 20 and len(dict_words) >= 3
                        and any(sep in password for sep in "-_. "))

    findings: list[dict] = []
    if is_common:
        findings.append(common_checker.common_password_finding())
    if leet_hit:
        findings.append(common_checker.leetspeak_finding())
    if dictionary_hit:
        findings.append(common_checker.dictionary_finding(dict_words))

    findings.extend(pattern_detector.run_pattern_checks(
        password, common_checker.DICTIONARY_WORDS,
        common_checker.COMMON_PASSWORDS))

    # Predictable-structure check on the leetspeak-normalized form too.
    if leet_hit and not any(f["type"] == "predictable_structure"
                            for f in findings):
        leet_structure = pattern_detector.detect_predictable_structure(
            leet, common_checker.DICTIONARY_WORDS,
            common_checker.COMMON_PASSWORDS)
        if leet_structure:
            leet_structure["detail"] += (" (Detected after normalizing "
                                         "letter-for-symbol substitutions.)")
            findings.append(leet_structure)

    context_findings = context_checker.check_context_overlap(password, context)
    findings.extend(context_findings)

    breach = breach_checker.check_breach_exposure(password, breach_hashes)
    if breach["found"]:
        findings.insert(0, breach_checker.breach_finding())

    score_info = compute_score(
        length=len(password),
        character_type_count=char_info["character_type_count"],
        unique_character_ratio=char_info["unique_character_ratio"],
        pool_size=pool_size,
        findings=findings,
        is_common=is_common,
        dictionary_hit=dictionary_hit,
        breach_found=breach["found"],
        dictionary_penalty=4 if passphrase_style else None,
    )

    suggestions = generate_suggestions(
        findings=findings,
        length=len(password),
        character_type_count=char_info["character_type_count"],
    )

    policy_result = evaluate_policy(
        password,
        is_common=is_common,
        personal_info_found=bool(context_findings),
        policy=policy,
    )

    return {
        "score": score_info["score"],
        "classification": score_info["classification"],
        "findings": findings,
        "suggestions": suggestions,
        "metrics": {
            "length": length_info,
            "characters": char_info,
            "entropy": entropy_info,
            "passphrase_style_detected": passphrase_style,
            "guess_resistance": guess_resistance_label(
                entropy_info["entropy_bits"]),
            "score_breakdown": {
                "contributions": score_info["contributions"],
                "penalties": score_info["penalties"],
                "total_penalty": score_info["total_penalty"],
                "breach_cap_applied": score_info["breach_cap_applied"],
            },
        },
        "breach_check": breach,
        "policy": policy_result,
        "disclaimer": _disclaimer(),
    }
