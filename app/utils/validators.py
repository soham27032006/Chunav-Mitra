"""
Module: validators.py
Purpose: Input validation and sanitization helpers for all Chunav Mitra API endpoints.
         Every public function raises a well-typed HTTPException so that route
         handlers stay concise and security rules are defined in one place.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

import re

from fastapi import HTTPException

from app.utils.constants import (
    INDIAN_STATES,
    MAX_NAME_LENGTH,
    MAX_QUERY_LENGTH,
    SUPPORTED_LANGUAGES,
    SUPPORTED_TOPICS,
)

__all__ = [
    "validate_query",
    "validate_name",
    "validate_pincode",
    "validate_state",
    "validate_language",
    "validate_topic",
]

# ── Alias map used by validate_topic ─────────────────────────────────────────
_TOPIC_ALIASES: dict[str, str] = {
    "evm": "EVM",
    "nota": "NOTA",
    "manifesto": "Manifesto",
    "voter id": "Voter ID",
    "voter_id": "Voter ID",
    "booth": "Booth",
    "election commission": "Election Commission",
    "election_commission": "Election Commission",
    "model code": "Model Code",
    "mcc": "Model Code",
    "vote counting": "Vote Counting",
    "counting": "Vote Counting",
}

# Characters considered dangerous in freeform text fields
_DANGEROUS_CHARS_RE = re.compile(r"[<>{}|\[\]\\]")


def validate_query(query: str) -> str:
    """Validate and sanitize a user chat query.

    Strips dangerous HTML/template characters to prevent injection, and
    enforces minimum length and maximum length constraints.

    Args:
        query: Raw query string submitted by the user.

    Returns:
        Sanitized query string with dangerous characters removed.

    Raises:
        HTTPException: HTTP 400 when the query is empty or exceeds
            ``MAX_QUERY_LENGTH`` characters.

    Example:
        >>> validate_query("What is a polling booth?")
        'What is a polling booth?'
        >>> validate_query("")  # raises HTTPException 400
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    if len(query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long. Max {MAX_QUERY_LENGTH} characters.",
        )
    return _DANGEROUS_CHARS_RE.sub("", query).strip()


def validate_name(name: str) -> str:
    """Validate and sanitize a voter full name.

    Allows Latin letters, Hindi/Devanagari characters (U+0900–U+097F),
    spaces, hyphens, and dots. All other characters are stripped.

    Args:
        name: Full voter name submitted by the user.

    Returns:
        Sanitized voter name with excess whitespace collapsed.

    Raises:
        HTTPException: HTTP 400 when the name is shorter than 2 characters,
            exceeds ``MAX_NAME_LENGTH``, or contains only invalid characters.

    Example:
        >>> validate_name("Priya Singh")
        'Priya Singh'
        >>> validate_name("A")  # raises HTTPException 400
    """
    if not name or len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters.")
    if len(name) > MAX_NAME_LENGTH:
        raise HTTPException(status_code=400, detail="Name too long.")
    sanitized = re.sub(r"[^a-zA-Z\s\u0900-\u097F\-\.]", "", name)
    cleaned = re.sub(r"\s+", " ", sanitized).strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Name contains only invalid characters.")
    return cleaned


def validate_pincode(pincode: str) -> str:
    """Validate an Indian six-digit postal code.

    Args:
        pincode: Candidate pincode string from the client.

    Returns:
        The validated six-digit pincode string unchanged.

    Raises:
        HTTPException: HTTP 400 when the pincode is not exactly six digits.

    Example:
        >>> validate_pincode("110001")
        '110001'
        >>> validate_pincode("1234")  # raises HTTPException 400
    """
    if not re.match(r"^\d{6}$", pincode):
        raise HTTPException(status_code=400, detail="Invalid pincode. Must be 6 digits.")
    return pincode


def validate_state(state: str, valid_states: list[str] | None = None) -> str:
    """Validate an Indian state or union territory name.

    Performs an exact case-sensitive match against the canonical list of
    28 Indian states and 8 UTs defined in ``INDIAN_STATES``.

    Args:
        state: State or UT name submitted by the client.
        valid_states: Optional override allowlist. Defaults to ``INDIAN_STATES``.

    Returns:
        The normalised state name as supplied (no transformation applied).

    Raises:
        HTTPException: HTTP 400 when the state name is not in the allowlist.

    Example:
        >>> validate_state("Delhi")
        'Delhi'
        >>> validate_state("NotAState")  # raises HTTPException 400
    """
    normalised = state.strip()
    states = valid_states if valid_states is not None else INDIAN_STATES
    if normalised not in states:
        raise HTTPException(status_code=400, detail=f"Invalid state: {state}")
    return normalised


def validate_language(lang: str | None) -> str:
    """Validate a requested UI/response language code.

    Args:
        lang: Two-letter language code (e.g. ``"en"`` or ``"hi"``),
              or ``None`` to use the default language.

    Returns:
        A supported language code string.

    Raises:
        HTTPException: HTTP 400 when the supplied code is not in
            ``SUPPORTED_LANGUAGES``.

    Example:
        >>> validate_language("hi")
        'hi'
        >>> validate_language(None)
        'en'
        >>> validate_language("fr")  # raises HTTPException 400
    """
    if lang is None:
        return SUPPORTED_LANGUAGES[0]
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
    return lang


def validate_topic(topic: str) -> str:
    """Validate and normalise an election topic for the explain endpoint.

    Accepts both canonical names (e.g. ``"EVM"``) and common aliases
    (e.g. ``"evm"``, ``"counting"``). Rejects anything that is not a
    recognised election topic.

    Args:
        topic: Topic string submitted by the client.

    Returns:
        Canonical topic name resolved from ``SUPPORTED_TOPICS``.

    Raises:
        HTTPException: HTTP 400 when the topic is empty, too long, or not
            in the list of supported election topics.

    Example:
        >>> validate_topic("EVM")
        'EVM'
        >>> validate_topic("evm")   # alias accepted
        'EVM'
        >>> validate_topic("INVALID")  # raises HTTPException 400
    """
    if not topic or not topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    if len(topic.strip()) > 100:
        raise HTTPException(status_code=400, detail="Topic too long.")
    sanitized = _DANGEROUS_CHARS_RE.sub("", topic).strip()
    normalised = _TOPIC_ALIASES.get(sanitized.lower(), sanitized)
    if normalised not in SUPPORTED_TOPICS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown topic. Choose from: {SUPPORTED_TOPICS}",
        )
    return normalised
