"""
Module: ask.py
Description: Chat route handlers for Chunav Mitra.
Author: Chunav Mitra Team
Version: 1.0.0
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

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])


def build_local_intent_response(intent: str, query: str = "", lang: str = "en") -> str | None:
    """Return a short local fallback for common intents.

    Args:
        intent: Classified user intent.
        query: Sanitized query text.
        lang: Preferred response language.

    Returns:
        A local response string when a direct answer is available, otherwise ``None``.
    """
    q = query.lower()
    responses = {
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

    if intent == "explain":
        if "evm" in q:
            return (
                "ईवीएम वोट देने की मशीन है जहाँ आप अपना अंतिम फैसला दर्ज करते हैं। "
                "इसे शादी के उस पल जैसा समझिए जब शगुन सही जोड़े को दिया जाता है। "
                "डिक्शनरी पेज पर EVM का पूरा समझाया हुआ रूप देख सकते हैं।"
                if lang == "hi"
                else "EVM is the machine where your final voting choice gets recorded. "
                "Shaadi analogy mein ise us pal ki tarah samjho jab shagun sahi couple ko diya jata hai. "
                "Dictionary page par EVM ka full explanation mil jayega."
            )
        if "nota" in q:
            return (
                "NOTA ka matlab hota hai ki voter kisi bhi candidate ko choose nahi karna chahta. "
                "Shaadi analogy mein yeh us guest jaisa hai jo menu dekh kar kehta hai ki mujhe koi dish pasand nahi aayi. "
                "Dictionary page par NOTA aur details mil jayengi."
                if lang == "en"
                else "नोटा का मतलब होता है कि मतदाता किसी भी उम्मीदवार को चुनना नहीं चाहता। "
                "शादी की मिसाल में यह उस मेहमान जैसा है जो मेन्यू देखकर कहे कि उसे कोई डिश पसंद नहीं आई। "
                "डिक्शनरी पेज पर NOTA की पूरी जानकारी मिल जाएगी।"
            )

    if intent in responses:
        return responses[intent].get(lang, responses[intent][DEFAULT_LANGUAGE])
    return None


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    """Answer a user chat query with safe validation and persistence."""
    try:
        sanitized_query = validate_query(req.query)
        session_id = req.session_id or create_session()
        lang = validate_language(req.lang) if req.lang else detect_language(sanitized_query)
        english_query = translate_to_english(sanitized_query) if lang == "hi" else sanitized_query

        intent_result = gemini_service.classify_intent(english_query)
        intent = str(intent_result["intent"])
        history = get_history(session_id) if req.session_id else []

        if len(history) > MAX_HISTORY_LENGTH:
            summary = gemini_service.summarize_history(history)
            english_query = f"[Conversation summary: {summary}]\n\nUser question: {english_query}"
            history = []

        english_response = build_local_intent_response(intent, english_query, lang)
        if english_response is None:
            english_response = gemini_service.ask_gemini(english_query, history)

        final_response = translate_to_hindi(english_response) if lang == "hi" else english_response

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
