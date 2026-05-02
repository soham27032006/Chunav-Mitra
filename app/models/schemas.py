"""
Module: schemas.py
Purpose: Pydantic request and response models for all Chunav Mitra API endpoints.
         Centralises field definitions, validation constraints, and OpenAPI
         documentation descriptions in one authoritative location.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

__all__ = [
    "AskRequest",
    "AskResponse",
    "VoterCheckRequest",
    "VoterCheckResponse",
    "BoothRequest",
    "BoothResponse",
    "TimelinePhase",
    "TimelineResponse",
    "ExplainRequest",
    "ExplainResponse",
    "StatsResponse",
    "TranscribeResponse",
    "TranslateRequest",
    "TranslateResponse",
]

# ── Type aliases ──────────────────────────────────────────────────────────────
LanguageCode = Literal["en", "hi"]
"""Supported response language codes."""

IntentType = Literal["voter_check", "booth_finder", "timeline", "explain", "general"]
"""Supported user-intent classification labels."""


# ── Chat ──────────────────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    """Request payload for the POST /api/ask chat endpoint.

    Attributes:
        query: The user's election question in Hindi or English.
        user_id: Optional caller identifier used for analytics.
        session_id: Optional existing session id for conversation continuity.
        lang: Optional explicit language preference; auto-detected when absent.
    """

    query: str = Field(..., description="User chat query in Hindi or English.")
    user_id: str | None = Field(default=None, description="Optional user identifier.")
    session_id: str | None = Field(default=None, description="Existing chat session id.")
    lang: LanguageCode | None = Field(default=None, description="Preferred response language.")


class AskResponse(BaseModel):
    """Response payload for the POST /api/ask chat endpoint.

    Attributes:
        response: AI-generated answer using shaadi analogies.
        detected_lang: Language code of the detected/preferred response.
        intent: Classified intent of the user query.
        session_id: Session identifier for follow-up queries.
    """

    response: str = Field(..., description="AI response text.")
    detected_lang: LanguageCode = Field(..., description="Response language code.")
    intent: IntentType = Field(..., description="Classified query intent.")
    session_id: str | None = Field(default=None, description="Chat session identifier.")


# ── Voter check ───────────────────────────────────────────────────────────────
class VoterCheckRequest(BaseModel):
    """Request payload for the POST /api/check-voter endpoint.

    Attributes:
        name: Full name of the voter to look up.
        state: Indian state or UT name to scope the search.
        dob: Optional date of birth in DD/MM/YYYY format.
    """

    name: str = Field(..., description="Full voter name.")
    state: str = Field(..., description="Indian state or UT.")
    dob: str | None = Field(default=None, description="Date of birth in DD/MM/YYYY format.")


class VoterCheckResponse(BaseModel):
    """Response payload for the POST /api/check-voter endpoint.

    Attributes:
        found: ``True`` when a voter record appears to exist.
        message: Human-friendly message with shaadi analogy.
        voter_id: Voter ID string when found, else ``None``.
    """

    found: bool = Field(..., description="Whether the voter was found.")
    message: str = Field(..., description="Shaadi-analogy response message.")
    voter_id: str | None = Field(default=None, description="Voter ID if found.")


# ── Booth finder ──────────────────────────────────────────────────────────────
class BoothRequest(BaseModel):
    """Request payload for the POST /api/find-booth endpoint.

    At least one of ``pincode`` or (``lat`` + ``lng``) must be provided.

    Attributes:
        pincode: Six-digit Indian postal code to search by.
        lat: GPS latitude coordinate from the user's device.
        lng: GPS longitude coordinate from the user's device.
    """

    pincode: str | None = Field(default=None, description="Six-digit Indian pincode.")
    lat: float | None = Field(default=None, description="GPS latitude.")
    lng: float | None = Field(default=None, description="GPS longitude.")


class BoothResponse(BaseModel):
    """Response payload for the POST /api/find-booth endpoint.

    Attributes:
        booth_name: Name of the nearest polling booth or landmark.
        address: Street address of the polling booth.
        distance: Approximate distance from the search origin.
        maps_link: URL to view the booth on a map.
        message: Human-friendly message with shaadi analogy.
        lat: Latitude of the booth location.
        lng: Longitude of the booth location.
    """

    booth_name: str = Field(..., description="Booth or landmark name.")
    address: str = Field(..., description="Booth street address.")
    distance: str = Field(..., description="Approximate distance from user.")
    maps_link: str = Field(..., description="Map URL for the booth location.")
    message: str = Field(..., description="Shaadi-analogy message.")
    lat: float | None = Field(default=None, description="Booth latitude.")
    lng: float | None = Field(default=None, description="Booth longitude.")


# ── Timeline ──────────────────────────────────────────────────────────────────
class TimelinePhase(BaseModel):
    """Representation of a single election phase milestone.

    Attributes:
        phase: Phase number (0 = announcement, 8 = results).
        name: Short display name for the phase.
        date: ISO 8601 date string (YYYY-MM-DD).
        description: Detailed description with shaadi analogy.
    """

    phase: int = Field(..., description="Phase sequence number.")
    name: str = Field(..., description="Phase display name.")
    date: str = Field(..., description="Phase date in YYYY-MM-DD format.")
    description: str = Field(..., description="Phase description.")


class TimelineResponse(BaseModel):
    """Response payload for the GET /api/timeline endpoint.

    Attributes:
        current_phase: Display name of the active or next phase.
        phases: Complete ordered list of election phases.
        next_deadline: Date of the upcoming milestone.
        days_remaining: Days until the next milestone.
        key_stats: High-level statistics about the 2024 election.
        election_year: Year of the featured election.
        lok_sabha_number: Ordinal number of the Lok Sabha formed.
    """

    current_phase: str = Field(..., description="Current or next phase name.")
    phases: list[TimelinePhase] = Field(..., description="All election phases.")
    next_deadline: str = Field(..., description="Next milestone date.")
    days_remaining: int = Field(..., description="Days to next milestone.")
    key_stats: dict[str, str] = Field(default_factory=dict, description="Election key stats.")
    election_year: str = Field(default="2024", description="Featured election year.")
    lok_sabha_number: str = Field(default="18th", description="Lok Sabha ordinal.")


# ── Explain / dictionary ──────────────────────────────────────────────────────
class ExplainRequest(BaseModel):
    """Request payload for the POST /api/explain endpoint.

    Attributes:
        topic: Election term to explain (must be in SUPPORTED_TOPICS).
        lang: Response language code.
    """

    topic: str = Field(..., description="Election topic to explain.")
    lang: LanguageCode = Field(default="en", description="Response language.")


class ExplainResponse(BaseModel):
    """Response payload for the POST /api/explain endpoint.

    Attributes:
        topic: Canonical topic name that was explained.
        shaadi_analogy: Desi wedding analogy for the topic.
        simple_explanation: Plain-language explanation.
        action_step: Recommended action for the voter.
        fun_fact: Interesting related fact.
        lang: Language code of the response.
    """

    topic: str = Field(..., description="Explained topic name.")
    shaadi_analogy: str = Field(..., description="Wedding analogy for the topic.")
    simple_explanation: str = Field(..., description="Plain-language explanation.")
    action_step: str = Field(..., description="Voter action step.")
    fun_fact: str = Field(..., description="Fun election fact.")
    lang: LanguageCode = Field(..., description="Response language code.")


# ── Analytics ─────────────────────────────────────────────────────────────────
class StatsResponse(BaseModel):
    """Response payload for the GET /api/stats endpoint.

    Attributes:
        total_queries: Cumulative number of queries logged.
        top_intents: Mapping of intent label to query count.
        languages_used: Mapping of language code to query count.
        queries_today: Number of queries logged since midnight UTC.
        most_asked_intent: Intent with the highest query count.
    """

    total_queries: int = Field(..., description="Total queries logged.")
    top_intents: dict[str, int] = Field(..., description="Intent counts.")
    languages_used: dict[str, int] = Field(..., description="Language counts.")
    queries_today: int = Field(..., description="Queries since midnight UTC.")
    most_asked_intent: str = Field(..., description="Most frequent intent.")


# ── Transcription ─────────────────────────────────────────────────────────────
class TranscribeResponse(BaseModel):
    """Response payload for the POST /api/transcribe endpoint.

    Attributes:
        text: Transcribed text from the audio input.
        lang: Detected language code of the transcription.
    """

    text: str = Field(..., description="Transcribed text.")
    lang: LanguageCode = Field(..., description="Detected language code.")


# ── Translation ───────────────────────────────────────────────────────────────
class TranslateRequest(BaseModel):
    """Request payload for the POST /api/translate endpoint.

    Attributes:
        texts: List of text strings to translate.
        target_lang: Target language code for all supplied strings.
    """

    texts: list[str] = Field(..., description="List of strings to translate.")
    target_lang: LanguageCode = Field(..., description="Target language code.")


class TranslateResponse(BaseModel):
    """Response payload for the POST /api/translate endpoint.

    Attributes:
        texts: Translated strings in the same order as the request.
        target_lang: Language code of the translations.
    """

    texts: list[str] = Field(..., description="Translated strings.")
    target_lang: LanguageCode = Field(..., description="Target language code.")
