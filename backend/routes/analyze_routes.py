"""
POST /api/analyze (PDF section 23).

Request:  { "password": "<processed transiently>", "context": {...}?,
            "policy": {...}? }
Response: { "score": 74, "classification": "STRONG", "findings": [...],
            "suggestions": [...], "metrics": {...}, "policy": {...}, ... }

Privacy contract enforced here:
  * the password is processed in memory only
  * it is never logged
  * it is never written to the database (only safe aggregate metadata is)
  * it never appears in error messages or in the response
"""
from __future__ import annotations

from fastapi import APIRouter

from ..models.schemas import AnalyzeRequest
from ..services.analytics_service import record_analysis
from ..services.password_analyzer import analyze_password

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze")
def analyze(req: AnalyzeRequest) -> dict:
    context = req.context.model_dump() if req.context else None
    policy = ({k: v for k, v in req.policy.model_dump().items()
               if v is not None} if req.policy else None)

    result = analyze_password(req.password, context=context, policy=policy)

    # Password is discarded here (goes out of scope); only metadata persists.
    # Empty submissions are not recorded — they carry no analytic value.
    analysis_id = (None if result["metrics"]["length"]["length"] == 0
                   else record_analysis(result))
    result["meta"] = {
        "privacy": ("Password was processed in memory only. It was not "
                    "logged, not stored, and is not included in this "
                    "response."),
        "analytics_recorded": analysis_id is not None,
    }
    return result
