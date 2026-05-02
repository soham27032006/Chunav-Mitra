"""
Module: transcribe.py
Description: Speech-to-text routes for Chunav Mitra.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import requests

from app.models.schemas import TranscribeResponse
from app.utils.logger import get_logger
from app.utils.validators import validate_language

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["transcribe"])

load_dotenv(override=True)
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
ENV_VALUES = dotenv_values(ENV_PATH)
GEMINI_API_KEY = ENV_VALUES.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY", "")
GEMINI_TRANSCRIBE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


def _build_transcription_prompt(lang: str) -> str:
    """Build a concise transcription-only prompt."""
    if lang == "hi":
        return (
            "Transcribe this Indian speech audio into plain Hindi text only. "
            "Return only the spoken words with no explanation."
        )
    return (
        "Transcribe this Indian speech audio into plain English text only. "
        "Return only the spoken words with no explanation."
    )


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    lang: str = Form("en"),
) -> TranscribeResponse:
    """Transcribe uploaded audio using Gemini multimodal input."""
    try:
        preferred_lang = validate_language(lang)
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=422, detail="No audio received")
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=503, detail="Speech service unavailable")

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": _build_transcription_prompt(preferred_lang)},
                        {
                            "inline_data": {
                                "mime_type": audio.content_type or "audio/webm",
                                "data": base64.b64encode(audio_bytes).decode("utf-8"),
                            }
                        },
                    ]
                }
            ]
        }
        response = requests.post(
            GEMINI_TRANSCRIBE_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
        if not text:
            raise HTTPException(status_code=422, detail="Could not understand audio")
        return TranscribeResponse(text=text, lang=preferred_lang)
    except HTTPException:
        raise
    except requests.HTTPError as error:
        logger.error("Transcription provider error: %s", error)
        raise HTTPException(status_code=503, detail="Speech service unavailable") from error
    except Exception as error:
        logger.error("Error in transcribe endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
