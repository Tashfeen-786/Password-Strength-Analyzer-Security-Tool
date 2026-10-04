"""
Password Policy Checker (PDF section 34).

Evaluates a submitted password against a configurable organizational policy.

Default policy (modern, NIST SP 800-63B / OWASP ASVS influenced):

    minimum_length:            12
    maximum_supported_length:  128
    common_passwords:          rejected
    personal_info_check:       rejected (against provided demo context)
    allow_spaces:              True

Modern password-policy principles:
  * Length matters more than forced composition rules.
  * Do not require arbitrary periodic password changes unless compromise
    is suspected or confirmed.
  * Reject known-common / breached passwords.

POLICY PASS / POLICY FAIL is reported SEPARATELY from the strength SCORE:
policy compliance and password strength are different concepts.
"""
from __future__ import annotations

DEFAULT_POLICY = {
    "minimum_length": 12,
    "maximum_length": 128,
    "common_password_check": True,
    "personal_info_check": True,
    "allow_spaces": True,
}


def evaluate_policy(password: str, *, is_common: bool,
                    personal_info_found: bool,
                    policy: dict | None = None) -> dict:
    """Evaluate the password against the policy. Returns PASS/FAIL + rules."""
    merged = {**DEFAULT_POLICY, **(policy or {})}
    length = len(password)
    rules: list[dict] = []

    min_len = int(merged["minimum_length"])
    rules.append({
        "rule": f"Minimum length {min_len}",
        "passed": length >= min_len,
        "detail": f"Length is {length} (minimum {min_len}).",
    })

    max_len = int(merged["maximum_length"])
    rules.append({
        "rule": f"Maximum supported length {max_len}",
        "passed": length <= max_len,
        "detail": f"Length is {length} (maximum supported {max_len}).",
    })

    if merged["common_password_check"]:
        rules.append({
            "rule": "Common passwords rejected",
            "passed": not is_common,
            "detail": ("Password is not a known common password."
                       if not is_common else
                       "Password appears in the common-password list."),
        })

    if merged["personal_info_check"]:
        rules.append({
            "rule": "Personal information rejected",
            "passed": not personal_info_found,
            "detail": ("No provided personal info detected in the password."
                       if not personal_info_found else
                       "Provided personal info appears in the password."),
        })

    if merged["allow_spaces"]:
        rules.append({
            "rule": "Spaces allowed",
            "passed": True,
            "detail": "Policy permits spaces (passphrase friendly).",
        })

    passed = all(r["passed"] for r in rules)
    return {
        "policy_result": "POLICY PASS" if passed else "POLICY FAIL",
        "passed": passed,
        "policy": merged,
        "rules": rules,
        "note": ("Policy compliance (PASS/FAIL) is shown separately from the "
                 "strength score: they are different concepts."),
    }
