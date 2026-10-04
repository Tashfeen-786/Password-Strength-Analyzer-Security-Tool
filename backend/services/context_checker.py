"""
Optional personal-context overlap check (PDF section 12).

The user may *voluntarily* provide demo context (first name, birth year,
company/college name). The comparison happens locally, in memory, and the
context is never stored. Only synthetic demo context should be used.

Example: Name "Rahul", password "Rahul@123"
Finding: "Password appears to contain personal information."
"""
from __future__ import annotations


def check_context_overlap(password: str, context: dict | None) -> list[dict]:
    """Return findings for overlaps between the password and demo context.

    context keys: first_name, birth_year, organization
    """
    if not context:
        return []
    lowered = password.lower()
    findings: list[dict] = []

    checks = [
        ("first_name", "First name in password", "personal_info_name"),
        ("organization", "Organization name in password", "personal_info_org"),
    ]
    for key, title, ftype in checks:
        value = (context.get(key) or "").strip().lower()
        if len(value) >= 3 and value in lowered:
            findings.append({
                "type": ftype,
                "severity": "high",
                "title": "Personal information detected",
                "description": "Password appears to contain personal information.",
                "detail": (f"{title}: attackers commonly try names and other "
                           "predictable personal information first."),
            })

    birth_year = str(context.get("birth_year") or "").strip()
    if len(birth_year) == 4 and birth_year.isdigit() and birth_year in password:
        findings.append({
            "type": "personal_info_year",
            "severity": "high",
            "title": "Personal information detected",
            "description": "Password appears to contain personal information.",
            "detail": ("Password contains the provided birth year — one of "
                       "the most commonly guessed values."),
        })
    return findings
