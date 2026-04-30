from fastapi import APIRouter
from app.models.schemas import VoterCheckRequest, VoterCheckResponse

router = APIRouter(prefix="/api", tags=["voter"])

@router.post("/check-voter", response_model=VoterCheckResponse)
async def check_voter(req: VoterCheckRequest):
    """
    Voter roll lookup with shaadi analogy response.

    For production: integrate ECI API → https://electoralsearch.eci.gov.in/
    For hackathon demo: mock with realistic shaadi messaging.

    ECI real endpoint (when available):
    POST https://electoralsearch.eci.gov.in/api/search
    Body: { "name": str, "state_code": str, "dob": str }
    """

    # ── MOCK LOGIC (replace with real ECI API call) ──────────────────
    # Simulate: found if name has 4+ chars and state is provided
    found = len(req.name.strip()) >= 4 and len(req.state.strip()) >= 2

    if found:
        message = (
            f"Wah wah! '{req.name}' ji, aapka naam "
            f"{req.state} ki Guest List (Electoral Roll) mein hai! "
            f"Aap is baar ki desh ki badi shaadi mein officially invited hain. "
            f"Ab sirf apna Mandap (Polling Booth) dhundho aur vote do — "
            f"yahi sabse bada shagun hai!"
        )
    else:
        message = (
            f"Oops! '{req.name}' ka naam abhi Guest List (Electoral Roll) mein "
            f"nahi mila. Ghabrao mat! "
            f"ECI website (electoralsearch.eci.gov.in) pe check karo ya "
            f"Form 6 bharke apna naam add karo. "
            f"Bina Guest List ke Mandap tak nahi pahuncho ge!"
        )

    return VoterCheckResponse(
        found=found,
        message=message,
        voter_id=f"{''.join(req.state[:3].upper())}{''.join(req.name[:3].upper())}12345" if found else None,
    )
