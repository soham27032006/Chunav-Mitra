"""
Module: stats.py
Description: Analytics routes for Chunav Mitra.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from collections import Counter
from datetime import UTC, date, datetime

from fastapi import APIRouter, HTTPException

from app.models.schemas import StatsResponse
from app.services.firebase_service import _mock_analytics, db
from app.utils.cache import cache
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["stats"])


def _load_analytics_records() -> list[dict[str, object]]:
    """Load analytics records from Firebase or mock storage."""
    if db:
        records: list[dict[str, object]] = []
        for doc in db.collection("analytics").stream():
            data = doc.to_dict()
            records.append(
                {
                    "intent": data.get("intent", "general"),
                    "lang": data.get("lang", "en"),
                    "timestamp": data.get("timestamp"),
                }
            )
        return records
    return list(_mock_analytics)


@router.get("/stats", response_model=StatsResponse)
async def get_stats() -> StatsResponse:
    """Return high-level analytics summaries."""
    try:
        cache_key = cache.make_key("stats")
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

        records = _load_analytics_records()
        total_queries = len(records)
        intent_counts = Counter(str(record["intent"]) for record in records)
        language_counts = Counter(str(record["lang"]) for record in records)
        today_start = datetime.combine(date.today(), datetime.min.time(), tzinfo=UTC)
        queries_today = sum(
            1 for record in records if record.get("timestamp") and record["timestamp"] >= today_start
        )

        response = StatsResponse(
            total_queries=total_queries,
            top_intents=dict(intent_counts.most_common()),
            languages_used=dict(language_counts.most_common()),
            queries_today=queries_today,
            most_asked_intent=intent_counts.most_common(1)[0][0] if intent_counts else "general",
        )
        cache.set(cache_key, response, ttl_seconds=60)
        return response
    except Exception as error:
        logger.error("Error in stats endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error


@router.get("/stats/detailed")
async def get_detailed_stats() -> dict[str, object]:
    """Return detailed analytics for dashboard-style views."""
    try:
        records = _load_analytics_records()
        daily_breakdown: dict[str, int] = {}
        hourly_distribution: Counter[int] = Counter()
        intent_by_language: dict[str, dict[str, int]] = {}

        for record in records:
            timestamp = record.get("timestamp")
            intent = str(record.get("intent", "general"))
            lang = str(record.get("lang", "en"))

            if timestamp:
                record_date = timestamp.date().isoformat()
                daily_breakdown[record_date] = daily_breakdown.get(record_date, 0) + 1
                hourly_distribution[timestamp.hour] += 1

            intent_by_language.setdefault(intent, {})
            intent_by_language[intent][lang] = intent_by_language[intent].get(lang, 0) + 1

        return {
            "daily_breakdown": daily_breakdown,
            "hourly_distribution": dict(hourly_distribution),
            "intent_by_language": intent_by_language,
        }
    except Exception as error:
        logger.error("Error in detailed stats endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
