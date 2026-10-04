"""
POST /api/generate-password (PDF sections 19, 23).

Cryptographically secure (secrets-based) password & passphrase generation.
The generated value is returned once and NEVER stored or logged; it is
demonstration output and should not be reused verbatim across accounts.
"""
from __future__ import annotations

from fastapi import APIRouter

from ..models.schemas import GenerateRequest
from ..services.password_generator import (generate_password,
                                           generate_passphrase)

router = APIRouter(prefix="/api", tags=["generator"])


@router.post("/generate-password")
def generate(req: GenerateRequest) -> dict:
    if req.mode == "passphrase":
        value = generate_passphrase(words=req.words, separator=req.separator)
        kind = "passphrase"
    else:
        value = generate_password(req.length, uppercase=req.uppercase,
                                  lowercase=req.lowercase, numbers=req.numbers,
                                  symbols=req.symbols)
        kind = "password"
    return {
        "mode": kind,
        "generated": value,
        "note": ("Generated with Python's 'secrets' module (CSPRNG). This "
                 "value was not stored or logged — it is demonstration "
                 "output; do not reuse demo passwords verbatim."),
        "privacy": "Nothing about this request is persisted.",
    }
