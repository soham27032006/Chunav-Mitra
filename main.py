"""
Module: main.py
Description: FastAPI application entrypoint for the Chunav Mitra backend.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.routes import ask, booth, explain, stats, timeline, transcribe, translate, voter
from app.routes.ask import build_local_intent_response
from app.services import gemini_service
from app.services.firebase_service import create_session, get_history, log_query, save_message
from app.services.translate_service import detect_language, translate_to_english, translate_to_hindi
from app.utils.constants import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
from app.utils.logger import get_logger
from app.utils.validators import validate_language, validate_query

settings = get_settings()
logger = get_logger(__name__)

# ── Keep-alive self-ping interval (seconds) ──────────────────────────────────
_KEEP_ALIVE_INTERVAL: int = 600  # 10 minutes


async def _keep_alive_ping() -> None:
    """Periodically ping our own /health endpoint to prevent Render cold starts.

    Runs as a background task for the lifetime of the application. Failures
    are silently logged — the main server is unaffected.
    """
    render_url = os.getenv("RENDER_EXTERNAL_URL", "")
    if not render_url:
        logger.info("RENDER_EXTERNAL_URL not set — keep-alive ping disabled.")
        return
    health_url = f"{render_url}/health"
    logger.info("Keep-alive ping enabled → %s every %ds", health_url, _KEEP_ALIVE_INTERVAL)
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            await asyncio.sleep(_KEEP_ALIVE_INTERVAL)
            try:
                resp = await client.get(health_url)
                logger.debug("Keep-alive ping → %s %d", health_url, resp.status_code)
            except Exception as exc:
                logger.warning("Keep-alive ping failed: %s", exc)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: startup and shutdown logic."""
    logger.info("Starting Chunav Mitra API v2.0.0")
    current_settings = get_settings()
    if not current_settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not configured!")
    logger.info("Environment: %s", current_settings.app_env)
    logger.info("CORS origins: %s", current_settings.origins_list)
    logger.info("Chunav Mitra ready! Jai Hind! 🇮🇳")
    # Start keep-alive background task
    keep_alive_task = asyncio.create_task(_keep_alive_ping())
    yield
    # Shutdown: cancel background task
    keep_alive_task.cancel()
    try:
        await keep_alive_task
    except asyncio.CancelledError:
        pass
    logger.info("Chunav Mitra shutting down. Alvida! 🙏")


app = FastAPI(
    title="Chunav Mitra API",
    description="Election Assistant with Desi Shaadi Analogies for Google Prompt Wars 2026.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_origin_regex=settings.allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
# NOTE: Middleware is executed in reverse registration order (LIFO stack).
# RateLimitMiddleware is added first so it runs innermost.
# SecurityHeadersMiddleware is added last so it wraps everything and applies
# security headers even to 429 rate-limit responses.
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)





@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Attach processing time header to every response.

    Args:
        request: Incoming HTTP request.
        call_next: Next middleware or route handler.

    Returns:
        Response with X-Process-Time header in milliseconds.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


app.include_router(ask.router)
app.include_router(voter.router)
app.include_router(booth.router)
app.include_router(timeline.router)
app.include_router(explain.router)
app.include_router(stats.router)
app.include_router(transcribe.router)
app.include_router(translate.router)


@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request) -> Response:
    """Return API metadata and important endpoints.

    Supports both GET (full body) and HEAD (headers only) methods so
    that uptime monitors and health-check probes receive a 200 response
    regardless of which HTTP method they use.

    Returns:
        JSON response with API name, tagline, and endpoint listing.
    """
    body = {
        "name": "Chunav Mitra",
        "tagline": "Aap desh ki sabse badi shaadi ke sabse zaroori guest hain!",
        "endpoints": {
            "chat": "POST /api/ask",
            "chat_stream": "GET /api/ask/stream?query=...&session_id=...",
            "voter": "POST /api/check-voter",
            "booth": "POST /api/find-booth",
            "timeline": "GET /api/timeline",
            "explain": "POST /api/explain",
            "transcribe": "POST /api/transcribe",
            "translate": "POST /api/translate",
            "stats": "GET /api/stats",
        },
        "docs": "/docs",
    }
    if request.method == "HEAD":
        return Response(status_code=200, media_type="application/json")
    return JSONResponse(content=body)


@app.api_route("/health", methods=["GET", "HEAD"])
async def health(request: Request) -> Response:
    """Return a lightweight healthcheck payload.

    Supports both GET and HEAD methods. HEAD returns headers only,
    which is the standard behaviour expected by uptime monitors.

    Returns:
        JSON response with status and current environment.
    """
    body = {"status": "healthy", "env": settings.app_env}
    if request.method == "HEAD":
        return Response(status_code=200, media_type="application/json")
    return JSONResponse(content=body)


@app.get("/api/ask/stream")
async def ask_stream(
    query: str = Query(..., description="User query string."),
    session_id: Optional[str] = Query(None, description="Session id for chat history."),
    user_id: Optional[str] = Query(None, description="Optional user id."),
    lang: Optional[str] = Query(None, description="Preferred response language."),
):
    """Stream a Gemini response over Server-Sent Events.

    Args:
        query: The user's question or message.
        session_id: Optional existing chat session identifier.
        user_id: Optional user identifier for tracking.
        lang: Optional language preference ('en' or 'hi').

    Returns:
        StreamingResponse with SSE chunks containing response text.

    Raises:
        HTTPException: On validation errors (400) or server errors (500).
    """
    try:
        sanitized_query = validate_query(query)
        preferred_lang = validate_language(lang) if lang else detect_language(sanitized_query)
        session = session_id or create_session()
        normalized_query = (
            translate_to_english(sanitized_query) if preferred_lang == "hi" else sanitized_query
        )
        history = get_history(session) if session_id else []
        intent_result = gemini_service.classify_intent(normalized_query)
        intent = str(intent_result["intent"])

        async def generate_stream():
            """Generate SSE chunks for the streaming response."""
            full_response: list[str] = []
            try:
                local_response = build_local_intent_response(intent, normalized_query, preferred_lang)
                if local_response:
                    full_response.append(local_response)
                    yield f"data: {json.dumps({'chunk': local_response, 'session_id': session, 'done': False, 'intent': intent})}\n\n"
                else:
                    async for chunk in gemini_service.ask_gemini_stream(normalized_query, history):
                        full_response.append(chunk)
                        yield f"data: {json.dumps({'chunk': chunk, 'session_id': session, 'done': False, 'intent': intent})}\n\n"

                complete_response = "".join(full_response).strip()
                final_response = (
                    translate_to_hindi(complete_response)
                    if preferred_lang == "hi" and complete_response
                    else complete_response
                )
                if final_response:
                    save_message(session, "user", sanitized_query, user_id)
                    save_message(session, "model", final_response, user_id)
                    log_query(session, intent, preferred_lang)

                yield f"data: {json.dumps({'chunk': '', 'session_id': session, 'done': True, 'intent': intent})}\n\n"
            except Exception as error:
                logger.error("Error in ask_stream generator: %s", error)
                payload = {
                    "chunk": "Kuch technical issue aa gaya. Please try again.",
                    "session_id": session,
                    "done": True,
                    "intent": intent,
                }
                yield f"data: {json.dumps(payload)}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "X-Session-ID": session,
                "X-Detected-Lang": preferred_lang,
                "X-Intent": intent,
            },
        )
    except HTTPException:
        raise
    except Exception as error:
        logger.error("Error in ask_stream endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=True)
