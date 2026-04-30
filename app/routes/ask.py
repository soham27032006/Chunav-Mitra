from fastapi import APIRouter
from app.models.schemas import AskRequest, AskResponse
from app.services.gemini_service import ask_gemini, classify_intent, summarize_history
from app.services.translate_service import detect_language, translate_to_english, translate_to_hindi
from app.services.firebase_service import save_message, get_history, create_session, log_query

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    # Create session if new
    session_id = req.session_id or create_session()

    # 1. Detect language ("hi", "en", etc.)
    lang = detect_language(req.query)

    # 2. Translate to English for Gemini (works best in English)
    en_query = translate_to_english(req.query) if lang == "hi" else req.query

    # 3. Classify intent (returns dict with intent and confidence)
    intent_result = classify_intent(en_query)
    intent = intent_result["intent"]

    # 4. Get chat history for multi-turn context
    history = get_history(session_id) if req.session_id else []

    # 5. Summarize history if too long (>10 messages)
    if len(history) > 10:
        summary = summarize_history(history)
        en_query = f"[Previous conversation summary: {summary}]\n\nUser question: {en_query}"
        # Reset history after summarization
        history = []

    # 6. Ask Gemini
    en_response = ask_gemini(en_query, history)

    # 7. Translate response back to user's language
    final = translate_to_hindi(en_response) if lang == "hi" else en_response

    # 8. Persist to Firestore
    save_message(session_id, "user", req.query, req.user_id)
    save_message(session_id, "model", final, req.user_id)
    log_query(session_id, intent, lang)

    return AskResponse(
        response=final,
        detected_lang=lang,
        intent=intent,
        session_id=session_id,
    )
