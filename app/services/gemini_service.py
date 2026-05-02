"""
Module: gemini_service.py
Description: AI service for Chunav Mitra using Google Gemini API.
Provides election guidance with Desi Wedding (Shaadi) analogies.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values, load_dotenv
import google.generativeai as genai

from app.utils.constants import MAX_HISTORY_LENGTH
from app.utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv(override=True)

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
ENV_VALUES = dotenv_values(ENV_PATH)
GEMINI_API_KEY = ENV_VALUES.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not configured. AI responses may be unavailable.")

SHAADI_SYSTEM_PROMPT = """
You are "Chunav Mitra" - India's friendliest election guide who explains
the Indian election process using Desi Wedding (Shaadi) analogies.
Use plain Hindi when the user prefers Hindi and plain English otherwise.

Rules:
- Keep answers short, warm, and practical.
- Use one clear wedding analogy.
- Stay neutral and never persuade toward any party or candidate.
- End with one helpful action suggestion.

ADDITIONAL CONTEXT:
- India has 970 million+ registered voters
- 543 Lok Sabha constituencies
- Voting age: 18 years
- ECI conducts elections: eci.gov.in
- Voter helpline: 1950
- Voter registration: nvsp.in

ALWAYS mention official resources:
- Voter search: electoralsearch.eci.gov.in
- Registration: nvsp.in  
- Helpline: 1950
"""

PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = ["gemini-flash-latest", "gemma-3-4b-it"]


def build_model(model_name: str) -> genai.GenerativeModel:
    """Create a configured Gemini model client.

    Args:
        model_name: Gemini model name to initialize.

    Returns:
        Configured ``GenerativeModel`` instance.

    Raises:
        ValueError: When the model name is empty.

    Example:
        >>> build_model("gemini-2.5-flash")
    """
    if not model_name.strip():
        raise ValueError("model_name cannot be empty.")
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SHAADI_SYSTEM_PROMPT,
    )


def classify_intent(query: str) -> dict[str, float | str]:
    """Classify the most likely user intent from a text query.

    Args:
        query: User query text.

    Returns:
        Intent dictionary with ``intent`` and ``confidence`` keys.

    Raises:
        ValueError: When the query is invalid.

    Example:
        >>> classify_intent("Where is my polling booth?")
        {'intent': 'booth_finder', 'confidence': 0.91}
    """
    if not isinstance(query, str):
        raise ValueError("Query must be a string.")

    q = query.lower()
    if any(word in q for word in ["voter", "list", "roll", "register", "naam", "मतदाता"]):
        return {"intent": "voter_check", "confidence": 0.92}
    if any(word in q for word in ["booth", "polling", "mandap", "kahan", "where"]):
        return {"intent": "booth_finder", "confidence": 0.91}
    if any(word in q for word in ["timeline", "phase", "date", "when", "kab", "counting"]):
        return {"intent": "timeline", "confidence": 0.9}
    if any(word in q for word in ["what", "explain", "how", "kya", "batao", "evm", "nota"]):
        return {"intent": "explain", "confidence": 0.84}
    return {"intent": "general", "confidence": 0.7}


def summarize_history(history: list[dict[str, Any]]) -> str:
    """Summarize recent chat history for long-running conversations.

    Args:
        history: Prior message history in Gemini-compatible format.

    Returns:
        Short summary string, or an empty string on failure.

    Raises:
        ValueError: When history is not a list.

    Example:
        >>> summarize_history([])
        ''
    """
    if not isinstance(history, list):
        raise ValueError("history must be a list.")
    if not history:
        return ""
    try:
        summary_model = genai.GenerativeModel(PRIMARY_MODEL)
        history_text = "\n".join(
            f"{item['role']}: {item['parts'][0]}" for item in history[-MAX_HISTORY_LENGTH:]
        )
        response = summary_model.generate_content(
            f"Summarize this conversation in 2 concise sentences:\n{history_text}"
        )
        return _get_response_text(response)
    except Exception as error:
        logger.warning("History summarization failed: %s", error)
        return ""


def _get_response_text(response: Any) -> str:
    """Extract normalized text from a Gemini response object.

    Args:
        response: Gemini response object.

    Returns:
        Stripped response text.

    Raises:
        ValueError: When the response object is invalid.

    Example:
        >>> _get_response_text(type('R', (), {'text': 'hello'})())
        'hello'
    """
    if response is None:
        raise ValueError("response cannot be None.")
    text = getattr(response, "text", "") or ""
    return text.strip()


def _quota_like_error(error: Exception) -> bool:
    """Detect whether an exception looks like a quota or rate-limit error.

    Args:
        error: Exception instance to inspect.

    Returns:
        ``True`` when the error looks quota-related, else ``False``.

    Raises:
        ValueError: When the error object is invalid.

    Example:
        >>> _quota_like_error(Exception("429 quota exceeded"))
        True
    """
    if error is None:
        raise ValueError("error cannot be None.")
    message = str(error).lower()
    return "quota exceeded" in message or "429" in message or "rate limit" in message


def _build_gemini_history(history: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Convert stored chat history into Gemini history payloads.

    Args:
        history: Previously stored chat history.

    Returns:
        Gemini-compatible history list.
    """
    if not history:
        return []
    return [
        {"role": item["role"], "parts": [item["parts"][0]]}
        for item in history[-MAX_HISTORY_LENGTH:]
    ]


def ask_gemini_with_fallback(query: str, history: list[dict[str, Any]] | None = None) -> str:
    """Request a Gemini response with model failover.

    Args:
        query: User query in the target model language.
        history: Optional prior chat history.

    Returns:
        Model response text.

    Raises:
        ValueError: When the query is invalid.
        RuntimeError: When all model attempts fail.

    Example:
        >>> ask_gemini_with_fallback("What is a voter ID?")
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string.")

    last_error: Exception | None = None
    gemini_history = _build_gemini_history(history)

    for model_name in [PRIMARY_MODEL, *FALLBACK_MODELS]:
        try:
            current_model = build_model(model_name)
            if gemini_history:
                chat = current_model.start_chat(history=gemini_history)
                response = chat.send_message(query)
            else:
                response = current_model.generate_content(query)
            text = _get_response_text(response)
            if text:
                return text
            last_error = RuntimeError(f"Empty response from model {model_name}")
        except Exception as error:
            last_error = error
            logger.warning("Gemini request failed on %s: %s", model_name, error)
            if not _quota_like_error(error):
                break

    raise RuntimeError("AI service is temporarily unavailable.") from last_error


def ask_gemini(query: str, history: list[dict[str, Any]] | None = None) -> str:
    """Return a non-streaming Gemini answer for a user query.

    Args:
        query: User query in the target model language.
        history: Optional prior chat history.

    Returns:
        Final response text or a sanitized fallback message.

    Raises:
        ValueError: When the query is invalid.

    Example:
        >>> ask_gemini("How do I vote?")
    """
    try:
        return ask_gemini_with_fallback(query, history)
    except Exception as error:
        logger.error("ask_gemini failed: %s", error)
        return "Kuch technical issue aa gaya. Please try again."


async def ask_gemini_stream(
    query: str,
    history: list[dict[str, Any]] | None = None,
):
    """Stream a Gemini response chunk-by-chunk.

    Args:
        query: User query in the target model language.
        history: Optional prior chat history.

    Yields:
        Streaming text chunks from Gemini, or one sanitized fallback chunk.

    Raises:
        ValueError: When the query is invalid.

    Example:
        >>> async for chunk in ask_gemini_stream("What is EVM?"):
        ...     print(chunk)
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string.")

    last_error: Exception | None = None
    gemini_history = _build_gemini_history(history)

    for model_name in [PRIMARY_MODEL, *FALLBACK_MODELS]:
        try:
            current_model = build_model(model_name)
            if gemini_history:
                chat = current_model.start_chat(history=gemini_history)
                response = await chat.send_message_async(query, stream=True)
            else:
                response = await current_model.generate_content_async(query, stream=True)
            async for chunk in response:
                text = getattr(chunk, "text", "")
                if text:
                    yield text
            return
        except Exception as error:
            last_error = error
            logger.warning("Gemini streaming failed on %s: %s", model_name, error)
            if not _quota_like_error(error):
                break

    logger.error("Gemini streaming failed completely: %s", last_error)
    yield "Kuch technical issue aa gaya. Please try again."
