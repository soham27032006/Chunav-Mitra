"""
Module: validators.py
Description: Input validation utilities for Chunav Mitra.
Author: Chunav Mitra Team
Version: 1.0.0
"""

import re

from fastapi import HTTPException

from app.utils.constants import INDIAN_STATES, MAX_QUERY_LENGTH, SUPPORTED_LANGUAGES


def validate_query(query: str) -> str:
    """Validate and sanitize a user query.

    Args:
        query: User-provided question text.

    Returns:
        Sanitized query text.

    Raises:
        HTTPException: If the query is empty or too long.
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    if len(query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long. Max {MAX_QUERY_LENGTH} characters.",
        )
    sanitized = re.sub(r"[<>{}\|\[\]\\]", "", query)
    return sanitized.strip()


def validate_pincode(pincode: str) -> str:
    """Validate Indian pincode format.

    Args:
        pincode: Candidate pincode string.

    Returns:
        The validated pincode.

    Raises:
        HTTPException: If the pincode is not a 6-digit Indian pincode.
    """
    if not re.match(r"^\d{6}$", pincode):
        raise HTTPException(status_code=400, detail="Invalid pincode. Must be 6 digits.")
    return pincode


def validate_name(name: str) -> str:
    """Validate and sanitize a voter name.

    Args:
        name: Candidate voter name.

    Returns:
        Sanitized voter name.

    Raises:
        HTTPException: If the name is too short or too long.
    """
    if not name or len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters.")
    if len(name) > 100:
        raise HTTPException(status_code=400, detail="Name too long.")
    sanitized = re.sub(r"[^a-zA-Z\s\u0900-\u097F]", "", name)
    return re.sub(r"\s+", " ", sanitized).strip()


def validate_state(state: str, valid_states: list[str] | None = None) -> str:
    """Validate an Indian state or union territory name.

    Args:
        state: Candidate state name.
        valid_states: Optional custom allowlist. Defaults to known Indian states/UTs.

    Returns:
        The normalized state string.

    Raises:
        HTTPException: If the state value is invalid.
    """
    normalized = state.strip()
    states = valid_states or INDIAN_STATES
    if normalized not in states:
        raise HTTPException(status_code=400, detail=f"Invalid state: {state}")
    return normalized


def validate_language(lang: str | None) -> str:
    """Validate a requested UI language.

    Args:
        lang: Optional language code.

    Returns:
        A supported language code.

    Raises:
        HTTPException: If the language is unsupported.
    """
    if lang is None:
        return SUPPORTED_LANGUAGES[0]
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
    return lang


def validate_topic(topic: str) -> str:
    """Validate topic text for dictionary/explainer requests.

    Args:
        topic: Topic string from the client.

    Returns:
        Sanitized topic string.

    Raises:
        HTTPException: If the topic is empty or too long.
    """
    if not topic or not topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    if len(topic.strip()) > 100:
        raise HTTPException(status_code=400, detail="Topic too long.")
    return re.sub(r"[<>{}\|\[\]\\]", "", topic).strip()
