"""
Safety helpers.

The single most important security property of this project:
submitted passwords are processed transiently, in memory, and are never
logged, persisted, echoed back in error messages, or placed in URLs.
"""
from __future__ import annotations

import re
from typing import Any


def redact(text: str, password: str) -> str:
    """Return `text` with every occurrence of `password` replaced by '[redacted]'.

    Defensive helper used by tests and error paths. The analyzer itself is
    designed so it never needs to include the password in any message.
    """
    if not password:
        return text
    return text.replace(password, "[redacted]")


def scrub_input_fields(payload: Any) -> Any:
    """Recursively remove 'input' values from pydantic-style error payloads.

    Pydantic v2 validation errors can embed the offending input value under
    an ``input`` key. For a password endpoint that would leak the password
    back into the HTTP response, so we strip those keys before responding.
    """
    if isinstance(payload, dict):
        return {k: ("[redacted]" if k == "input" else scrub_input_fields(v))
                for k, v in payload.items()}
    if isinstance(payload, list):
        return [scrub_input_fields(item) for item in payload]
    return payload


SAFE_TEXT_RE = re.compile(r"^[\x20-\x7E]*$")


def contains_password(text: str, password: str) -> bool:
    """True if `text` contains the (non-empty) password — used by privacy tests."""
    return bool(password) and password in text
