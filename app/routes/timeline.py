"""
Module: timeline.py
Description: Election timeline routes for Chunav Mitra.
Author: Chunav Mitra Team
Version: 2.0.0
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
        name="Lok Sabha Phase 1",
        date="2024-04-19",
        description="First phase of voting covering 102 constituencies across 21 states and UTs. The biggest phase of the election.",
    ),
    TimelinePhase(
        phase=2,
        name="Lok Sabha Phase 2",
        date="2024-04-26",
        description="Second phase covering 89 constituencies across 13 states. Shaadi ka dusra bada function!",
    ),
    TimelinePhase(
        phase=3,
        name="Lok Sabha Phase 3",
        date="2024-05-07",
        description="Third phase covering 94 constituencies in 12 states. The momentum continues.",
    ),
    TimelinePhase(
        phase=4,
        name="Lok Sabha Phase 4",
        date="2024-05-13",
        description="Fourth phase covering 96 constituencies across 10 states. Halfway through the grand festival.",
    ),
    TimelinePhase(
        phase=5,
        name="Lok Sabha Phase 5",
        date="2024-05-20",
        description="Fifth phase covering 49 constituencies across 8 states. Crucial battles taking place.",
    ),
    TimelinePhase(
        phase=6,
        name="Lok Sabha Phase 6",
        date="2024-05-25",
        description="Sixth phase covering 58 constituencies in 8 states. Reaching the final stages.",
    ),
    TimelinePhase(
        phase=7,
        name="Lok Sabha Phase 7",
        date="2024-06-01",
        description="Final phase covering 57 constituencies across 8 states. The last rituals before counting.",
    ),
    TimelinePhase(
        phase=8,
        name="Vote Counting Day",
        date="2024-06-04",
        description="Counting of votes and declaration of results. The ultimate finale of the grand Indian election wedding!",
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
