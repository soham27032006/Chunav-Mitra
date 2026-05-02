"""
Module: timeline.py
Description: Election timeline routes for Chunav Mitra.
Author: Chunav Mitra Team
Version: 1.0.0
"""

from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, HTTPException

from app.models.schemas import TimelinePhase, TimelineResponse
from app.utils.cache import cache
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["timeline"])

PHASES: list[TimelinePhase] = [
    TimelinePhase(
        phase=1,
        name="West Bengal Assembly Term Ends",
        date="2026-05-07",
        description="ECI ke official 2025-2026 assembly note ke hisaab se West Bengal Assembly ka term 7 May 2026 ko end hota hai.",
    ),
    TimelinePhase(
        phase=2,
        name="Tamil Nadu Assembly Term Ends",
        date="2026-05-10",
        description="Tamil Nadu Assembly ka current term 10 May 2026 tak hai, isliye election process is date se pehle complete hona chahiye.",
    ),
    TimelinePhase(
        phase=3,
        name="Assam Assembly Term Ends",
        date="2026-05-20",
        description="Assam Assembly ka term 20 May 2026 ko expire hota hai; official poll schedule ECI is deadline se pehle notify karta hai.",
    ),
    TimelinePhase(
        phase=4,
        name="Kerala Assembly Term Ends",
        date="2026-05-23",
        description="Kerala Assembly ka term 23 May 2026 tak valid hai. Naye House ka chunav is date se pehle complete hona zaroori hota hai.",
    ),
    TimelinePhase(
        phase=5,
        name="Puducherry Assembly Term Ends",
        date="2026-06-15",
        description="Puducherry Assembly ka term 15 June 2026 tak hai. ECI ki official process is deadline ke andar complete hoti hai.",
    ),
]


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline() -> TimelineResponse:
    """Return the current and upcoming election milestones."""
    try:
        cache_key = cache.make_key("timeline")
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

        today = date.today()
        current_phase = "Official election schedule awaited from ECI"
        next_deadline = "Awaiting ECI schedule announcement"
        days_remaining = 0

        for phase in PHASES:
            phase_date = datetime.strptime(phase.date, "%Y-%m-%d").date()
            if phase_date >= today:
                current_phase = phase.name
                next_deadline = phase.date
                days_remaining = (phase_date - today).days
                break

        response = TimelineResponse(
            current_phase=current_phase,
            phases=PHASES,
            next_deadline=next_deadline,
            days_remaining=days_remaining,
        )
        cache.set(cache_key, response, ttl_seconds=3600)
        return response
    except Exception as error:
        logger.error("Error in timeline endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
