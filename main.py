from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.config import get_settings
from app.routes import ask, voter, booth, timeline, explain, stats
from app.middleware.rate_limiter import RateLimitMiddleware
from app.services.gemini_service import ask_gemini_stream
from app.services.firebase_service import get_history, create_session
from app.services.translate_service import detect_language, translate_to_english, translate_to_hindi

settings = get_settings()

app = FastAPI(
    title="Chunav Mitra API",
    description="Election Assistant with Desi Shaadi Analogies — Google Prompt Wars 2026",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Register routers
app.include_router(ask.router)
app.include_router(voter.router)
app.include_router(booth.router)
app.include_router(timeline.router)
app.include_router(explain.router)
app.include_router(stats.router)

@app.get("/")
async def root():
    return {
        "name": "Chunav Mitra",
        "tagline": "Aap desh ki sabse badi shaadi ke sabse zaroori guest hain!",
        "endpoints": {
            "chat": "POST /api/ask",
            "chat_stream": "GET /api/ask/stream?query=...&session_id=...",
            "voter": "POST /api/check-voter",
            "booth": "POST /api/find-booth",
            "timeline": "GET /api/timeline",
            "explain": "POST /api/explain",
            "stats": "GET /api/stats",
        },
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.app_env}


@app.get("/api/ask/stream")
async def ask_stream(
    query: str = Query(..., description="User query string"),
    session_id: Optional[str] = Query(None, description="Session ID for chat history"),
    user_id: Optional[str] = Query(None, description="User ID")
):
    """
    Streaming chat endpoint that returns Gemini response as a stream.
    Useful for real-time chat experiences.
    """
    from app.services.firebase_service import save_message, log_query
    from app.services.gemini_service import classify_intent

    # Create session if needed
    sid = session_id or create_session()

    # Detect language
    lang = detect_language(query)

    # Translate to English for Gemini
    en_query = translate_to_english(query) if lang == "hi" else query

    # Get chat history
    history = get_history(sid) if session_id else []

    # Classify intent
    intent_result = classify_intent(en_query)
    intent = intent_result["intent"]

    async def generate_stream():
        """Generate SSE streaming response with translation if needed."""
        import json
        full_response = []

        # Stream chunks from Gemini
        async for chunk in ask_gemini_stream(en_query, history):
            full_response.append(chunk)
            # Yield SSE formatted chunk
            sse_data = json.dumps({
                "chunk": chunk,
                "session_id": sid,
                "done": False,
                "intent": intent
            })
            yield f"data: {sse_data}\n\n"

        # Combine full response
        complete_en_response = "".join(full_response)

        # Translate if needed
        if lang == "hi":
            final_response = translate_to_hindi(complete_en_response)
        else:
            final_response = complete_en_response

        # Save to Firestore
        try:
            save_message(sid, "user", query, user_id)
            save_message(sid, "model", final_response, user_id)
            log_query(sid, intent, lang)
        except Exception:
            pass  # Don't fail streaming if logging fails

        # Yield done signal
        done_data = json.dumps({
            "chunk": "",
            "session_id": sid,
            "done": True,
            "intent": intent
        })
        yield f"data: {done_data}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Session-ID": sid,
            "X-Detected-Lang": lang,
            "X-Intent": intent
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=True)
