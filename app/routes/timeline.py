"""
Module: timeline.py
Purpose: Election timeline routes for Chunav Mitra.
         Provides the official 2024 Indian General Election (18th Lok Sabha)
         phase schedule with shaadi analogies and key voting statistics.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, HTTPException

from app.models.schemas import TimelinePhase, TimelineResponse
from app.utils.cache import cache
from app.utils.logger import get_logger

__all__ = ["router", "get_timeline"]

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["timeline"])

# ── 2024 Lok Sabha (18th General Election) official phases ────────────────────
ELECTION_PHASES: list[TimelinePhase] = [
    TimelinePhase(
        phase=0,
        name="Announcement — Shaadi ka Card Bheja Gaya",
        date="2024-03-16",
        description=(
            "ECI announced the 2024 Lok Sabha election schedule on March 16. "
            "Model Code of Conduct came into effect immediately. "
            "Shaadi ka official card poore desh mein bhej diya gaya!"
        ),
    ),
    TimelinePhase(
        phase=1,
        name="Phase 1 Voting — Pehle Mangalphera",
        date="2024-04-19",
        description=(
            "Phase 1: 102 constituencies across 21 states and UTs voted. "
            "Includes Arunachal Pradesh, Sikkim, Meghalaya, and parts of Assam. "
            "Pehla mangalphera ho gaya — 66.14% voter turnout!"
        ),
    ),
    TimelinePhase(
        phase=2,
        name="Phase 2 Voting — Doosre Phere",
        date="2024-04-26",
        description=(
            "Phase 2: 89 constituencies across 13 states voted. "
            "Key states: Kerala, Karnataka, Rajasthan, Uttar Pradesh, Maharashtra. "
            "66.71% voter turnout recorded."
        ),
    ),
    TimelinePhase(
        phase=3,
        name="Phase 3 Voting — Teesre Phere",
        date="2024-05-07",
        description=(
            "Phase 3: 94 constituencies across 12 states voted. "
            "Includes Gujarat, Goa, Madhya Pradesh, Uttar Pradesh, Bihar, West Bengal, Assam. "
            "65.68% voter turnout."
        ),
    ),
    TimelinePhase(
        phase=4,
        name="Phase 4 Voting — Chauthe Phere",
        date="2024-05-13",
        description=(
            "Phase 4: 96 constituencies across 10 states voted. "
            "Key states: Andhra Pradesh, Telangana, UP, MP, Maharashtra, West Bengal, Odisha, Jharkhand. "
            "69.16% voter turnout — highest so far!"
        ),
    ),
    TimelinePhase(
        phase=5,
        name="Phase 5 Voting — Paanchve Phere",
        date="2024-05-20",
        description=(
            "Phase 5: 49 constituencies across 8 states voted. "
            "Includes Uttar Pradesh, Rajasthan, Madhya Pradesh, West Bengal. "
            "62.2% voter turnout recorded."
        ),
    ),
    TimelinePhase(
        phase=6,
        name="Phase 6 Voting — Chhathe Phere",
        date="2024-05-25",
        description=(
            "Phase 6: 58 constituencies across 7 states voted. "
            "Includes Delhi, Haryana, Uttar Pradesh, West Bengal, Odisha, Jharkhand, Bihar. "
            "63.36% voter turnout."
        ),
    ),
    TimelinePhase(
        phase=7,
        name="Phase 7 Voting — Antim Mangalphera",
        date="2024-06-01",
        description=(
            "Phase 7 FINAL: 57 constituencies across 8 states. "
            "Last phase completed! 642 million voters participated overall — highest ever! "
            "312 million women voters — a new democratic record!"
        ),
    ),
    TimelinePhase(
        phase=8,
        name="Results — Vidaai! Winner Announced",
        date="2024-06-04",
        description=(
            "Vote counting on June 4. NDA won 293 seats; BJP secured 240 seats. "
            "PM Modi's historic third term! 18th Lok Sabha formed. "
            "Desh ki shaadi complete — winner ki vidaai ho gayi!"
        ),
    ),
]

# ── Key statistics for the 2024 General Election ─────────────────────────────
KEY_STATS: dict[str, str] = {
    "total_voters": "968 million registered voters",
    "total_voted": "642 million voters participated",
    "women_voters": "312 million women voters (record)",
    "constituencies": "543 Lok Sabha seats",
    "phases": "7 voting phases",
    "duration": "April 19 to June 1, 2024 (44 days)",
    "result_date": "June 4, 2024",
    "winner": "NDA — 293 seats, PM Modi third term",
    "eci_website": "https://elections24.eci.gov.in",
    "results_website": "https://results.eci.gov.in",
    "voter_helpline": "1950",
    "voter_registration": "https://nvsp.in",
}


def _determine_current_phase() -> tuple[str, str, int]:
    """Calculate the current or upcoming phase based on today's date.

    Iterates through all phases in chronological order and returns the
    first phase whose date is on or after today. Falls back to a generic
    label when all phases have passed.

    Returns:
        A three-tuple of ``(current_phase_name, next_deadline_date, days_remaining)``.

    Example:
        >>> phase, deadline, days = _determine_current_phase()
        >>> isinstance(days, int)
        True
    """
    today = date.today()
    for phase in ELECTION_PHASES:
        phase_date = datetime.strptime(phase.date, "%Y-%m-%d").date()
        if phase_date >= today:
            return phase.name, phase.date, (phase_date - today).days
    return (
        "18th Lok Sabha in session — Next elections due by 2029",
        "2029-05-01",
        (date(2029, 5, 1) - today).days,
    )


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline() -> TimelineResponse:
    """Return the complete 2024 Indian General Election timeline and key stats.

    Serves a cached response for up to one hour to reduce repeated computation.
    The ``current_phase`` field reflects the nearest upcoming milestone based
    on the server's current date.

    Returns:
        ``TimelineResponse`` containing all Lok Sabha 2024 phases, the
        current/next phase label, days remaining, and aggregated election stats.

    Raises:
        HTTPException: HTTP 500 on unexpected server errors.

    Example:
        GET /api/timeline
        → {
            "current_phase": "18th Lok Sabha in session",
            "phases": [...],
            "key_stats": {"total_voters": "968 million", ...},
            "election_year": "2024",
            "lok_sabha_number": "18th"
          }
    """
    try:
        cache_key = cache.make_key("timeline_v2")
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

        current_phase, next_deadline, days_remaining = _determine_current_phase()

        response = TimelineResponse(
            current_phase=current_phase,
            phases=ELECTION_PHASES,
            next_deadline=next_deadline,
            days_remaining=days_remaining,
            key_stats=KEY_STATS,
            election_year="2024",
            lok_sabha_number="18th",
        )
        cache.set(cache_key, response, ttl_seconds=3600)
        return response
    except HTTPException:
        raise
    except Exception as error:
        logger.error("Error in timeline endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
