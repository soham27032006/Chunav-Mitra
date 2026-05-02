"""
Module: ask.py
Purpose: AI chat route handler for Chunav Mitra.
         Handles POST /api/ask — the primary conversational endpoint that
         accepts election questions in Hindi or English, calls Gemini AI with
         shaadi-analogy prompts, persists the exchange in Firestore, and
         returns structured responses.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import AskRequest, AskResponse
from app.services import gemini_service
from app.services.firebase_service import create_session, get_history, log_query, save_message
from app.services.translate_service import detect_language, translate_to_english, translate_to_hindi
from app.utils.constants import DEFAULT_LANGUAGE, MAX_HISTORY_LENGTH
from app.utils.logger import get_logger
from app.utils.validators import validate_language, validate_query

__all__ = ["router", "ask", "build_local_intent_response"]

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])

# ── Static local responses for high-confidence intents ────────────────────────
_LOCAL_RESPONSES: dict[str, dict[str, str]] = {
    "voter_check": {
        "en": (
            "Voter list bilkul shaadi ki guest list jaisi hoti hai. "
            "Naam confirm karna sabse pehla step hai, warna mandap tak pahunch kar bhi vote nahi de paoge. "
            "Guest List page par apna naam aur state daal kar check kijiye."
        ),
        "hi": (
            "मतदाता सूची बिल्कुल शादी की गेस्ट लिस्ट जैसी होती है। "
            "पहले अपना नाम पक्का कर लीजिए, वरना मंडप तक पहुँच कर भी वोट नहीं दे पाएंगे। "
            "गेस्ट लिस्ट पेज पर अपना नाम और राज्य डालकर जाँच कीजिए।"
        ),
    },
    "booth_finder": {
        "en": (
            "Polling booth aapka shaadi wala mandap hai. "
            "Vote dene se pehle sahi jagah ka pata hona bahut zaroori hai. "
            "Mandap page par pincode ya location se apna booth dhoondhiye."
        ),
        "hi": (
            "पोलिंग बूथ आपका शादी वाला मंडप है। "
            "वोट देने से पहले सही जगह का पता होना बहुत ज़रूरी है। "
            "मंडप पेज पर पिनकोड या लोकेशन से अपना बूथ ढूँढिए।"
        ),
    },
    "timeline": {
        "en": (
            "Election timeline shaadi ke function schedule ki tarah hoti hai. "
            "Har phase ka apna date aur role hota hai, isliye timeline dekhna planning ke liye useful hai. "
            "Timeline page par saari important dates mil jayengi."
        ),
        "hi": (
            "चुनाव की टाइमलाइन शादी के फ़ंक्शन शेड्यूल जैसी होती है। "
            "हर चरण की अपनी तारीख और भूमिका होती है, इसलिए टाइमलाइन देखना तैयारी के लिए उपयोगी है। "
            "टाइमलाइन पेज पर सभी महत्वपूर्ण तारीखें मिल जाएँगी।"
        ),
    },
}

# ── Inline EVM / NOTA responses ───────────────────────────────────────────────
_EVM_RESPONSE_EN = (
    "EVM is the machine where your final voting choice gets recorded. "
    "Shaadi analogy mein ise us pal ki tarah samjho jab shagun sahi couple ko diya jata hai. "
    "Dictionary page par EVM ka full explanation mil jayega."
)
_EVM_RESPONSE_HI = (
    "ईवीएम वोट देने की मशीन है जहाँ आप अपना अंतिम फैसला दर्ज करते हैं। "
    "इसे शादी के उस पल जैसा समझिए जब शगुन सही जोड़े को दिया जाता है। "
    "डिक्शनरी पेज पर EVM का पूरा समझाया हुआ रूप देख सकते हैं।"
)
_NOTA_RESPONSE_EN = (
    "NOTA ka matlab hota hai ki voter kisi bhi candidate ko choose nahi karna chahta. "
    "Shaadi analogy mein yeh us guest jaisa hai jo menu dekh kar kehta hai ki mujhe koi dish pasand nahi aayi. "
    "Dictionary page par NOTA aur details mil jayengi."
)
_NOTA_RESPONSE_HI = (
    "नोटा का मतलब होता है कि मतदाता किसी भी उम्मीदवार को चुनना नहीं चाहता। "
    "शादी की मिसाल में यह उस मेहमान जैसा है जो मेन्यू देखकर कहे कि उसे कोई डिश पसंद नहीं आई। "
    "डिक्शनरी पेज पर NOTA की पूरी जानकारी मिल जाएगी।"
)


def build_local_intent_response(intent: str, query: str = "", lang: str = "en") -> str | None:
    """Return a short deterministic fallback for common high-confidence intents.

    For well-understood intents such as voter list or booth lookup the function
    returns a pre-written shaadi-analogy response without calling the AI model.
    This keeps latency low and reduces token usage for simple requests.

    Args:
        intent: Classified user intent string from ``classify_intent``.
        query: Sanitised query text used for keyword-level EVM/NOTA detection.
        lang: Preferred response language code (``"en"`` or ``"hi"``).

    Returns:
        A localised response string when a local fallback exists, or ``None``
        when the intent requires a full Gemini AI call.

    Example:
        >>> build_local_intent_response("booth_finder", "", "en")
        'Polling booth aapka shaadi wala mandap hai...'
        >>> build_local_intent_response("general", "", "en") is None
        True
    """
    query_lower = query.lower()

    # ── Inline explain shortcuts for EVM and NOTA ──────────────────────────
    if intent == "explain":
        if "evm" in query_lower:
            return _EVM_RESPONSE_HI if lang == "hi" else _EVM_RESPONSE_EN
        if "nota" in query_lower:
            return _NOTA_RESPONSE_EN if lang == "en" else _NOTA_RESPONSE_HI

    # ── Pre-written responses for voter / booth / timeline ─────────────────
    if intent in _LOCAL_RESPONSES:
        return _LOCAL_RESPONSES[intent].get(lang, _LOCAL_RESPONSES[intent][DEFAULT_LANGUAGE])

    return None


def _build_query_with_summary(
    english_query: str,
    history: list[dict],
) -> tuple[str, list[dict]]:
    """Summarise long history and prepend to the query when needed.

    When conversation history exceeds ``MAX_HISTORY_LENGTH`` the function
    asks Gemini to summarise it and embeds the summary in the query so
    context is preserved without exceeding model limits.

    Args:
        english_query: Current English-language user query.
        history: Full conversation history list.

    Returns:
        A two-tuple of ``(augmented_query, trimmed_history)`` where history
        is reset to an empty list after summarisation.

    Example:
        >>> query, hist = _build_query_with_summary("hello", [])
        >>> hist == []
        True
    """
    if len(history) <= MAX_HISTORY_LENGTH:
        return english_query, history
    summary = gemini_service.summarize_history(history)
    augmented = f"[Conversation summary: {summary}]\n\nUser question: {english_query}"
    return augmented, []


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    """Process a user election query and return an AI-generated response.

    Accepts questions in Hindi or English. The pipeline:
    1. Validates and sanitises the query.
    2. Auto-detects the language when not explicitly supplied.
    3. Translates Hindi queries to English for classification and AI calls.
    4. Classifies the user intent.
    5. Attempts a local deterministic response first to save latency.
    6. Falls back to Gemini AI with shaadi-analogy system prompt.
    7. Translates the English response back to Hindi when needed.
    8. Persists the exchange to Firestore and logs analytics.

    Args:
        req: ``AskRequest`` containing the query, optional session_id,
             optional user_id, and optional language preference.

    Returns:
        ``AskResponse`` with the AI answer, detected language, classified
        intent, and the session identifier for follow-up queries.

    Raises:
        HTTPException: HTTP 400 when the query fails validation.
        HTTPException: HTTP 500 when the AI service is unavailable.

    Example:
        Request body: ``{"query": "Voter list mein naam kaise check karein?"}``
        Response: ``{"response": "...", "detected_lang": "hi", "intent": "voter_check", ...}``
    """
    try:
        # 1. Validate input
        sanitized_query = validate_query(req.query)
        session_id = req.session_id or create_session()

        # 2. Detect or validate language
        lang = validate_language(req.lang) if req.lang else detect_language(sanitized_query)

        # 3. Normalise to English for AI processing
        english_query = (
            translate_to_english(sanitized_query) if lang == "hi" else sanitized_query
        )

        # 4. Classify intent
        intent_result = gemini_service.classify_intent(english_query)
        intent = str(intent_result["intent"])

        # 5. Load conversation history (only when session already existed)
        history = get_history(session_id) if req.session_id else []

        # 6. Handle long conversations via summary
        english_query, history = _build_query_with_summary(english_query, history)

        # 7. Try local response; fall back to Gemini
        english_response = build_local_intent_response(intent, english_query, lang)
        if english_response is None:
            logger.info("Calling Gemini: intent=%s, lang=%s", intent, lang)
            english_response = gemini_service.ask_gemini(english_query, history)

        # 8. Translate response back to Hindi when needed
        final_response = (
            translate_to_hindi(english_response) if lang == "hi" else english_response
        )

        # 9. Persist exchange
        save_message(session_id, "user", sanitized_query, req.user_id)
        save_message(session_id, "model", final_response, req.user_id)
        log_query(session_id, intent, lang)

        return AskResponse(
            response=final_response,
            detected_lang=lang,
            intent=intent,  # type: ignore[arg-type]
            session_id=session_id,
        )
    except HTTPException:
        raise
    except Exception as error:
        logger.error("Error in ask endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
