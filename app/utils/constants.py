"""
Module: constants.py
Purpose: Application-wide constants for Chunav Mitra.
         Centralises all magic numbers, strings and lookup lists so
         that business rules are defined exactly once.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from typing import Final

__all__ = [
    "MAX_QUERY_LENGTH",
    "MAX_HISTORY_LENGTH",
    "DEFAULT_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "SUPPORTED_TOPICS",
    "INDIAN_STATES",
    "VOTER_HELPLINE",
    "ECI_WEBSITE",
    "ECI_VOTER_SEARCH",
    "ECI_RESULTS_WEBSITE",
    "NVSP_WEBSITE",
    "LOK_SABHA_SEATS",
    "REGISTERED_VOTERS",
]

# ── API limits ────────────────────────────────────────────────────────────────
MAX_QUERY_LENGTH: Final[int] = 500
"""Maximum permitted character length for a user chat query."""

MAX_NAME_LENGTH: Final[int] = 100
"""Maximum permitted character length for a voter name."""

MAX_HISTORY_LENGTH: Final[int] = 10
"""Maximum number of prior messages included in a Gemini chat session."""

RATE_LIMIT_PER_MINUTE: Final[int] = 30
"""Sliding-window request limit per client IP address."""

# ── Cache TTLs (seconds) ──────────────────────────────────────────────────────
CACHE_TTL_TIMELINE: Final[int] = 3600
"""Cache lifetime for timeline responses (1 hour)."""

CACHE_TTL_EXPLAIN: Final[int] = 86400
"""Cache lifetime for explain responses (24 hours)."""

CACHE_TTL_STATS: Final[int] = 60
"""Cache lifetime for analytics stats responses (1 minute)."""

# ── Language settings ─────────────────────────────────────────────────────────
SUPPORTED_LANGUAGES: Final[list[str]] = ["en", "hi"]
"""Language codes accepted by the translation and explain endpoints."""

DEFAULT_LANGUAGE: Final[str] = "en"
"""Fallback language code when detection is inconclusive."""

# ── Supported explanation topics ──────────────────────────────────────────────
SUPPORTED_TOPICS: Final[list[str]] = [
    "EVM",
    "NOTA",
    "Manifesto",
    "Voter ID",
    "Booth",
    "Election Commission",
    "Model Code",
    "Vote Counting",
]
"""Election topics that the /api/explain endpoint can explain with shaadi analogies."""

# ── Indian election facts ─────────────────────────────────────────────────────
LOK_SABHA_SEATS: Final[int] = 543
"""Total number of Lok Sabha (lower house) constituencies."""

REGISTERED_VOTERS: Final[str] = "968 million"
"""Approximate number of registered voters in the 2024 Indian General Election."""

VOTER_HELPLINE: Final[str] = "1950"
"""ECI national voter helpline number."""

ECI_WEBSITE: Final[str] = "https://eci.gov.in"
"""Official Election Commission of India website."""

ECI_VOTER_SEARCH: Final[str] = "https://electoralsearch.eci.gov.in"
"""ECI electoral roll search portal."""

ECI_RESULTS_WEBSITE: Final[str] = "https://results.eci.gov.in"
"""Official ECI results portal for the 2024 Lok Sabha election."""

NVSP_WEBSITE: Final[str] = "https://nvsp.in"
"""National Voter Service Portal for voter registration."""

# ── Indian states and union territories ───────────────────────────────────────
INDIAN_STATES: Final[list[str]] = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Puducherry",
    "Chandigarh",
    "Andaman and Nicobar",
    "Dadra and Nagar Haveli",
    "Daman and Diu",
    "Lakshadweep",
]
"""Complete list of 28 Indian states and 8 union territories."""
