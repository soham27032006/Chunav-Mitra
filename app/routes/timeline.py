from fastapi import APIRouter
from app.models.schemas import TimelineResponse, TimelinePhase
from datetime import datetime, date

router = APIRouter(prefix="/api", tags=["timeline"])

# ── Update these dates with real ECI election schedule ─────────────────────
PHASES: list[TimelinePhase] = [
    TimelinePhase(phase=1, name="Notification — Shaadi ka Card",   date="2024-03-20",
                  description="Official election announcement. ECI ne shaadi ka card bheja!"),
    TimelinePhase(phase=2, name="Nomination — Rishta Pakka",       date="2024-03-27",
                  description="Candidates file nominations. Dulha-Dulhan decide ho gaye."),
    TimelinePhase(phase=3, name="Scrutiny — Rishta Check",         date="2024-03-30",
                  description="Nomination papers checked. Background verification ho rahi hai."),
    TimelinePhase(phase=4, name="Withdrawal — Last Chance",        date="2024-04-02",
                  description="Last date to withdraw. Ab peeche nahi hat sakte!"),
    TimelinePhase(phase=5, name="Campaigning — Baraat",            date="2024-04-19",
                  description="Parties campaign. Baraat nikal rahi hai — shor machao!"),
    TimelinePhase(phase=6, name="Voting Day — Mangalphera",        date="2024-04-19",
                  description="THE day! Booth jao, vote do. Desh ki shaadi complete karo!"),
    TimelinePhase(phase=7, name="Counting — Saat Phere Result",    date="2024-06-04",
                  description="Votes counted. Winner announce — Vidaai ho gayi!"),
]

@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline():
    today = date.today()
    current_phase = "Election complete — agli shaadi ka intezaar!"
    next_deadline = "Check ECI website for next election dates"
    days_remaining = 0

    for phase in PHASES:
        phase_date = datetime.strptime(phase.date, "%Y-%m-%d").date()
        if phase_date >= today:
            current_phase = phase.name
            next_deadline = phase.date
            days_remaining = (phase_date - today).days
            break

    return TimelineResponse(
        current_phase=current_phase,
        phases=PHASES,
        next_deadline=next_deadline,
        days_remaining=days_remaining,
    )
