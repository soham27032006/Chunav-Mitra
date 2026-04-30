from fastapi import APIRouter
from app.models.schemas import StatsResponse
from app.services.firebase_service import db, _mock_analytics
from datetime import datetime, date, timedelta
from collections import Counter

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get analytics statistics from Firestore.
    Returns query counts, intent breakdown, language usage, and today's stats.
    """
    try:
        # Get all analytics documents
        if db:
            docs = db.collection("analytics").stream()
            all_records = []
            for doc in docs:
                data = doc.to_dict()
                all_records.append({
                    "intent": data.get("intent", "general"),
                    "lang": data.get("lang", "en"),
                    "timestamp": data.get("timestamp")
                })
        else:
            # Mock mode - use in-memory analytics
            all_records = _mock_analytics

        # Calculate total queries
        total_queries = len(all_records)

        # Calculate top intents
        intent_counts = Counter(r["intent"] for r in all_records)
        top_intents = dict(intent_counts.most_common())

        # Calculate languages used
        lang_counts = Counter(r["lang"] for r in all_records)
        languages_used = dict(lang_counts.most_common())

        # Calculate today's queries (UTC)
        today_start = datetime.combine(date.today(), datetime.min.time())
        queries_today = sum(
            1 for r in all_records
            if r["timestamp"] and r["timestamp"] >= today_start
        )

        # Determine most asked intent
        most_asked_intent = intent_counts.most_common(1)[0][0] if intent_counts else "general"

        return StatsResponse(
            total_queries=total_queries,
            top_intents=top_intents,
            languages_used=languages_used,
            queries_today=queries_today,
            most_asked_intent=most_asked_intent
        )

    except Exception as e:
        # Return empty stats on error
        return StatsResponse(
            total_queries=0,
            top_intents={},
            languages_used={},
            queries_today=0,
            most_asked_intent="general"
        )


@router.get("/stats/detailed")
async def get_detailed_stats():
    """
    Get detailed analytics with time-based breakdowns.
    Useful for dashboard visualizations.
    """
    try:
        docs = db.collection("analytics").stream()

        records_by_date = {}
        hourly_distribution = Counter()
        intent_by_language = {}

        for doc in docs:
            data = doc.to_dict()
            ts = data.get("timestamp")

            if ts:
                # Group by date
                record_date = ts.date().isoformat()
                if record_date not in records_by_date:
                    records_by_date[record_date] = 0
                records_by_date[record_date] += 1

                # Hourly distribution
                hour = ts.hour
                hourly_distribution[hour] += 1

            # Intent by language breakdown
            intent = data.get("intent", "general")
            lang = data.get("lang", "en")

            if intent not in intent_by_language:
                intent_by_language[intent] = {}
            if lang not in intent_by_language[intent]:
                intent_by_language[intent][lang] = 0
            intent_by_language[intent][lang] += 1

        return {
            "daily_breakdown": records_by_date,
            "hourly_distribution": dict(hourly_distribution),
            "intent_by_language": intent_by_language
        }

    except Exception:
        return {
            "daily_breakdown": {},
            "hourly_distribution": {},
            "intent_by_language": {}
        }
