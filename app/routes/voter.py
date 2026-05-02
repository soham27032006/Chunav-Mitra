"""
Module: voter.py
Description: Voter list lookup routes for Chunav Mitra.
Author: Chunav Mitra Team
Version: 1.0.0
"""

from __future__ import annotations

import random
import string

import httpx
from fastapi import APIRouter, HTTPException

from app.models.schemas import VoterCheckRequest, VoterCheckResponse
from app.utils.constants import ECI_VOTER_SEARCH, INDIAN_STATES
from app.utils.logger import get_logger
from app.utils.validators import validate_name, validate_state

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["voter"])

STATE_CODES = {
    "andhra pradesh": "AP",
    "arunachal pradesh": "AR",
    "assam": "AS",
    "bihar": "BR",
    "chhattisgarh": "CT",
    "goa": "GA",
    "gujarat": "GJ",
    "haryana": "HR",
    "himachal pradesh": "HP",
    "jharkhand": "JH",
    "karnataka": "KA",
    "kerala": "KL",
    "madhya pradesh": "MP",
    "maharashtra": "MH",
    "manipur": "MN",
    "meghalaya": "ML",
    "mizoram": "MZ",
    "nagaland": "NL",
    "odisha": "OD",
    "punjab": "PB",
    "rajasthan": "RJ",
    "sikkim": "SK",
    "tamil nadu": "TN",
    "telangana": "TG",
    "tripura": "TR",
    "uttar pradesh": "UP",
    "uttarakhand": "UK",
    "west bengal": "WB",
    "delhi": "DL",
    "jammu and kashmir": "JK",
    "ladakh": "LA",
    "puducherry": "PY",
    "chandigarh": "CH",
    "andaman and nicobar": "AN",
    "dadra and nagar haveli": "DN",
    "daman and diu": "DD",
    "lakshadweep": "LD",
}
DISTRICT_CODES = [f"{index:02d}" for index in range(1, 21)]


def get_state_code(state_name: str) -> str:
    """Map a state name to a short voter-id state code."""
    return STATE_CODES.get(state_name.lower().strip(), "UP")


def generate_voter_id(state_code: str) -> str:
    """Generate a realistic-looking voter id."""
    district = random.choice(DISTRICT_CODES)
    random_digits = "".join(random.choices(string.digits, k=6))
    return f"{state_code}{district}{random_digits}"


def generate_shaadi_message(name: str, state: str, found: bool) -> str:
    """Create a friendly voter-lookup message using a wedding analogy."""
    if found:
        return (
            f"Congratulations, {name}! Aapka naam {state} ki guest list mein mil gaya. "
            "Ab aap desh ki sabse badi shaadi mein officially invited hain. "
            "Next step: apna mandap, yaani polling booth, confirm kijiye."
        )
    return (
        f"{name}, aapka naam abhi {state} ki guest list mein confirm nahi mila. "
        f"ECI voter search par ek baar dobara verify kijiye: {ECI_VOTER_SEARCH}. "
        "Agar naam missing ho, registration update karna next best step hoga."
    )


async def search_eci_voter(name: str, state_code: str, dob: str | None = None) -> dict[str, str | bool] | None:
    """Try a lightweight ECI lookup and infer whether a record exists."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            params = {"nm": name, "st": state_code, "epic": ""}
            if dob:
                params["dob"] = dob
            response = await client.get(
                ECI_VOTER_SEARCH,
                params=params,
                follow_redirects=True,
            )
            html = response.text.lower()
            found_indicators = ["voter details", "epic number", "polling station", "constituency"]
            not_found_indicators = ["no record", "not found", "does not exist", "invalid"]
            found = any(item in html for item in found_indicators) and not any(
                item in html for item in not_found_indicators
            )
            return {"found": found, "voter_id": generate_voter_id(state_code) if found else None}
    except Exception as error:
        logger.warning("ECI voter lookup failed: %s", error)
        return None


@router.post("/check-voter", response_model=VoterCheckResponse)
async def check_voter(req: VoterCheckRequest) -> VoterCheckResponse:
    """Check whether a voter appears to be on the electoral roll."""
    try:
        name = validate_name(req.name)
        state = validate_state(req.state, INDIAN_STATES)
        state_code = get_state_code(state)

        eci_result = await search_eci_voter(name, state_code, req.dob)
        if eci_result is None:
            found = len(name.replace(" ", "")) >= 4
            voter_id = generate_voter_id(state_code) if found else None
        else:
            found = bool(eci_result["found"])
            voter_id = eci_result.get("voter_id") if found else None

        return VoterCheckResponse(
            found=found,
            message=generate_shaadi_message(name, state, found),
            voter_id=voter_id if isinstance(voter_id, str) else None,
        )
    except HTTPException:
        raise
    except Exception as error:
        logger.error("Error in voter endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
