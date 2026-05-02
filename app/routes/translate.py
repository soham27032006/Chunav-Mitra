"""
Module: translate.py
Description: Translation routes for Chunav Mitra.
Author: Chunav Mitra Team
Version: 1.0.0
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import TranslateRequest, TranslateResponse
from app.services.translate_service import translate_to
from app.utils.logger import get_logger
from app.utils.validators import validate_language

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["translate"])


@router.post("/translate", response_model=TranslateResponse)
async def translate_batch(req: TranslateRequest) -> TranslateResponse:
    """Translate a batch of texts into the requested language."""
    try:
        target_lang = validate_language(req.target_lang)
        translated_texts = [
            translate_to(text, target_lang) if isinstance(text, str) and text.strip() else text
            for text in req.texts
        ]
        return TranslateResponse(texts=translated_texts, target_lang=target_lang)
    except HTTPException:
        raise
    except Exception as error:
        logger.error("Error in translate endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
