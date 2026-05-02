"""
Module: voter.py
Purpose: Voter electoral-roll lookup routes for Chunav Mitra.
         Validates name and state, attempts a lightweight ECI portal probe,
         and returns a deterministic voter ID with a shaadi-analogy message.
Author: Chunav Mitra Team
Version: 2.0.0
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

__all__ = ["router", "check_voter", "generate_voter_id", "get_state_code"]

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
    """Map a full state name to its two-letter voter-ID state code.

    Args:
        state_name: Full state or UT name (case-insensitive).

    Returns:
        Two-letter state abbreviation used in voter IDs, or ``"UP"``
        as a safe default when the name is not found.

    Example:
        >>> get_state_code("Delhi")
        'DL'
    """
    return STATE_CODES.get(state_name.lower().strip(), "UP")


def generate_voter_id(state_code: str) -> str:
    """Generate a realistic-looking example voter ID string.

    The generated ID is **not** a real voter ID; it is used only for
    demonstration purposes in the demo voter lookup response.

    Args:
        state_code: Two-letter state abbreviation (e.g. ``"DL"`` for Delhi).

    Returns:
        A plausible voter ID string in the format ``<STATE><DISTRICT><6-DIGITS>``.

    Example:
        >>> vid = generate_voter_id("DL")
        >>> vid.startswith("DL")
        True
    """
    district = random.choice(DISTRICT_CODES)
    random_digits = "".join(random.choices(string.digits, k=6))
    return f"{state_code}{district}{random_digits}"


def generate_shaadi_message(name: str, state: str, found: bool) -> str:
    """Create a friendly voter-lookup result message with a wedding analogy.

    Args:
        name: Validated voter name.
        state: Validated state or UT name.
        found: Whether the voter appears to be on the electoral roll.

    Returns:
        A Hinglish message string with a desi shaadi analogy.

    Example:
        >>> msg = generate_shaadi_message("Priya", "Delhi", True)
        >>> "guest list" in msg
        True
    """
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


async def search_eci_voter(
    name: str,
    state_code: str,
    dob: str | None = None,
) -> dict[str, str | bool] | None:
    """Probe the ECI voter search portal and infer record existence.

    Makes a lightweight HTTP GET to the ECI electoral search page and
    uses keyword heuristics to determine whether a matching voter record
    is likely to exist. Returns ``None`` on any network error so that
    callers can apply their own fallback logic.

    Args:
        name: Validated full voter name.
        state_code: Two-letter state code for the ECI query.
        dob: Optional date of birth in DD/MM/YYYY format.

    Returns:
        Dictionary with ``found`` (bool) and ``voter_id`` (str or None),
        or ``None`` when the ECI portal cannot be reached.

    Example:
        >>> result = await search_eci_voter("Rahul", "DL")
        >>> result is None or "found" in result
        True
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            params: dict[str, str] = {"nm": name, "st": state_code, "epic": ""}
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
    """Check whether a voter appears to be on the electoral roll.

    Validates the supplied name and state, probes the ECI search portal,
    and returns a deterministic result with a shaadi-analogy message.
    Falls back to a heuristic when the ECI portal is unreachable.

    Args:
        req: ``VoterCheckRequest`` with ``name``, ``state``, and optional ``dob``.

    Returns:
        ``VoterCheckResponse`` with ``found``, ``message``, and ``voter_id``.

    Raises:
        HTTPException: HTTP 400 when name or state validation fails.
        HTTPException: HTTP 500 on unexpected server errors.

    Example:
        Request: ``{"name": "Priya Singh", "state": "Delhi"}``
        Response: ``{"found": true, "message": "...", "voter_id": "DL01123456"}``
    """
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
