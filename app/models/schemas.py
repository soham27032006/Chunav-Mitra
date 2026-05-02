"""
Module: schemas.py
Description: Pydantic request and response models for Chunav Mitra APIs.
Author: Chunav Mitra Team
Version: 1.0.0
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


LanguageCode = Literal["en", "hi"]
IntentType = Literal["voter_check", "booth_finder", "timeline", "explain", "general"]


class AskRequest(BaseModel):
    """Request payload for the chat endpoint."""

    query: str = Field(..., description="User chat query.")
    user_id: str | None = Field(default=None, description="Optional user identifier.")
    session_id: str | None = Field(default=None, description="Existing chat session id.")
    lang: LanguageCode | None = Field(default=None, description="Preferred response language.")


class AskResponse(BaseModel):
    """Response payload for the chat endpoint."""

    response: str
    detected_lang: LanguageCode
    intent: IntentType
    session_id: str | None = None


class VoterCheckRequest(BaseModel):
    """Request payload for voter lookup."""

    name: str
    state: str
    dob: str | None = Field(default=None, description="Optional date of birth in DD/MM/YYYY format.")


class VoterCheckResponse(BaseModel):
    """Response payload for voter lookup."""

    found: bool
    message: str
    voter_id: str | None = None


class BoothRequest(BaseModel):
    """Request payload for booth discovery."""

    pincode: str | None = None
    lat: float | None = None
    lng: float | None = None


class BoothResponse(BaseModel):
    """Response payload for booth discovery."""

    booth_name: str
    address: str
    distance: str
    maps_link: str
    message: str
    lat: float | None = None
    lng: float | None = None


class TimelinePhase(BaseModel):
    """One timeline milestone."""

    phase: int
    name: str
    date: str
    description: str


class TimelineResponse(BaseModel):
    """Timeline response payload."""

    current_phase: str
    phases: list[TimelinePhase]
    next_deadline: str
    days_remaining: int


class ExplainRequest(BaseModel):
    """Request payload for explain/dictionary endpoint."""

    topic: str
    lang: LanguageCode = "en"


class ExplainResponse(BaseModel):
    """Response payload for explain/dictionary endpoint."""

    topic: str
    shaadi_analogy: str
    simple_explanation: str
    action_step: str
    fun_fact: str
    lang: LanguageCode


class StatsResponse(BaseModel):
    """Response payload for analytics stats."""

    total_queries: int
    top_intents: dict[str, int]
    languages_used: dict[str, int]
    queries_today: int
    most_asked_intent: str


class TranscribeResponse(BaseModel):
    """Response payload for speech transcription."""

    text: str
    lang: LanguageCode


class TranslateRequest(BaseModel):
    """Request payload for bulk translation."""

    texts: list[str]
    target_lang: LanguageCode


class TranslateResponse(BaseModel):
    """Response payload for bulk translation."""

    texts: list[str]
    target_lang: LanguageCode
