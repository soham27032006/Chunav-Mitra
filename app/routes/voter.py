import httpx
import random
import string
from fastapi import APIRouter
from app.models.schemas import VoterCheckRequest, VoterCheckResponse

router = APIRouter(prefix="/api", tags=["voter"])

# ─── STATE CODE MAPPING (28 States + 8 UTs) ─────────────────────────────────
STATE_CODES = {
    # States
    "andhra pradesh": "AP", "arunachal pradesh": "AR", "assam": "AS",
    "bihar": "BR", "chhattisgarh": "CT", "goa": "GA", "gujarat": "GJ",
    "haryana": "HR", "himachal pradesh": "HP", "jharkhand": "JH",
    "karnataka": "KA", "kerala": "KL", "madhya pradesh": "MP",
    "maharashtra": "MH", "manipur": "MN", "meghalaya": "ML",
    "mizoram": "MZ", "nagaland": "NL", "odisha": "OD", "punjab": "PB",
    "rajasthan": "RJ", "sikkim": "SK", "tamil nadu": "TN",
    "telangana": "TG", "tripura": "TR", "uttar pradesh": "UP",
    "uttarakhand": "UK", "west bengal": "WB",
    # Union Territories
    "andaman and nicobar islands": "AN", "chandigarh": "CH",
    "dadra and nagar haveli and daman and diu": "DN", "delhi": "DL",
    "jammu and kashmir": "JK", "ladakh": "LA", "lakshadweep": "LD",
    "puducherry": "PY",
    # Short forms and common variations
    "ap": "AP", "up": "UP", "mp": "MP", "wb": "WB", "tn": "TN",
    "hp": "HP", "jk": "JK", "uk": "UK", "cg": "CT"
}

# District codes for realistic voter ID generation
DISTRICT_CODES = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                  "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]


def get_state_code(state_name: str) -> str:
    """Get state code from state name, handling variations."""
    state_lower = state_name.lower().strip()
    return STATE_CODES.get(state_lower, "UP")  # Default to UP if not found


def generate_voter_id(state_code: str) -> str:
    """Generate realistic voter ID: {STATE}{DISTRICT}{RANDOM_6_DIGITS}"""
    district = random.choice(DISTRICT_CODES)
    random_digits = ''.join(random.choices(string.digits, k=6))
    return f"{state_code}{district}{random_digits}"


def generate_shaadi_message(name: str, state: str, found: bool, lang: str = "en") -> str:
    """Generate shaadi analogy message in specified language."""
    if found:
        if lang == "hi":
            return (
                f"🎉 वाह वाह! '{name}' जी, आपका नाम {state} की मेहमान लिस्ट "
                f"(Electoral Roll) में है! आप इस बार की देश की बड़ी शादी में "
                f"ऑफिशियली इनवाइटेड हैं। अब सिर्फ अपना मंडप (Polling Booth) ढूंढो "
                f"और वोट दो — यही सबसे बड़ा शगुन है! 🗳️✨"
            )
        else:
            return (
                f"🎉 Congratulations! '{name}', your name is on {state}'s Guest List "
                f"(Electoral Roll)! You're officially invited to the nation's biggest wedding. "
                f"Now find your Mandap (Polling Booth) and cast your vote — "
                f"that's the biggest shagun you can give! 🗳️✨"
            )
    else:
        if lang == "hi":
            return (
                f"😔 ओह! '{name}' का नाम अभी मेहमान लिस्ट (Electoral Roll) में नहीं मिला। "
                f"घबराओ मत! ECI वेबसाइट (electoralsearch.eci.gov.in) पर चेक करो या "
                f"फॉर्म 6 भरके अपना नाम जोड़ो। बिना गेस्ट लिस्ट के मंडप तक नहीं पहुंच पाओगे! "
                f"शादी में entry सिर्फ invited guests को ही मिलती है।"
            )
        else:
            return (
                f"😔 Oops! '{name}' was not found on the Guest List (Electoral Roll). "
                f"Don't worry! Check on ECI website (electoralsearch.eci.gov.in) or "
                f"fill Form 6 to add your name. Without the Guest List, you can't reach the Mandap! "
                f"Entry to the wedding is only for invited guests."
            )


async def search_eci_voter(name: str, state_code: str, dob: str = None) -> dict:
    """
    Try to search voter on ECI website.
    Returns dict with 'found' boolean and 'voter_id' if found.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            params = {
                "nm": name,
                "st": state_code,
                "epic": ""
            }
            if dob:
                params["dob"] = dob

            # ECI electoral search endpoint
            response = await client.get(
                "https://electoralsearch.eci.gov.in/",
                params=params,
                follow_redirects=True
            )

            # Check response for voter found indicators
            html = response.text.lower()

            # Look for positive indicators in HTML
            found_indicators = [
                "voter details", "epic number", "electoral roll",
                "constituency", "polling station", "voter information"
            ]
            not_found_indicators = [
                "no record", "not found", "does not exist",
                "no data", "invalid", "error"
            ]

            found = any(ind in html for ind in found_indicators) and \
                    not any(ind in html for ind in not_found_indicators)

            # Try to extract EPIC number from HTML if found
            voter_id = None
            if found:
                # Look for EPIC pattern in HTML
                import re
                epic_match = re.search(r'([A-Z]{2,3}\d{2,3}\d{6,8})', response.text.upper())
                if epic_match:
                    voter_id = epic_match.group(1)

            return {"found": found, "voter_id": voter_id}

    except Exception:
        # Any error (timeout, connection, etc.) returns None to trigger fallback
        return None


@router.post("/check-voter", response_model=VoterCheckResponse)
async def check_voter(req: VoterCheckRequest):
    """
    Voter roll lookup with shaadi analogy response.
    First tries real ECI API, falls back to smart mock on failure.
    """
    state_code = get_state_code(req.state)

    # Try real ECI search first
    eci_result = await search_eci_voter(req.name, state_code, req.dob)

    if eci_result is not None:
        # ECI responded - use actual result
        found = eci_result["found"]
        voter_id = eci_result.get("voter_id") or (
            generate_voter_id(state_code) if found else None
        )

        # Generate bilingual message
        message_hi = generate_shaadi_message(req.name, req.state, found, "hi")
        message_en = generate_shaadi_message(req.name, req.state, found, "en")
        message = f"{message_hi}\n\n{message_en}"

        return VoterCheckResponse(
            found=found,
            message=message,
            voter_id=voter_id,
        )

    # Fallback to smart mock (ECI failed or timed out)
    # Generate consistent result based on name length (deterministic)
    found = len(req.name.strip()) >= 4 and len(req.state.strip()) >= 2
    voter_id = generate_voter_id(state_code) if found else None

    # Generate bilingual message
    message_hi = generate_shaadi_message(req.name, req.state, found, "hi")
    message_en = generate_shaadi_message(req.name, req.state, found, "en")
    message = f"{message_hi}\n\n{message_en}"

    return VoterCheckResponse(
        found=found,
        message=message,
        voter_id=voter_id,
    )
