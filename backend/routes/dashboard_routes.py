"""
Dashboard / analytics endpoints (PDF sections 21, 23).

  GET /api/dashboard/stats        -> aggregate statistics (never passwords)
  GET /api/analytics/weaknesses   -> weakness type + pattern frequency
"""
from __future__ import annotations

from fastapi import APIRouter

from ..services.analytics_service import (get_dashboard_stats,
                                          get_weakness_analytics)

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/dashboard/stats")
def dashboard_stats() -> dict:
    return get_dashboard_stats()


@router.get("/analytics/weaknesses")
def analytics_weaknesses() -> dict:
    return get_weakness_analytics()
