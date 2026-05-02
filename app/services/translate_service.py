"""
Module: translate_service.py
Description: Translation utilities for Chunav Mitra.
Provides language detection and Google-powered translation helpers.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from langdetect import detect
from deep_translator import GoogleTranslator

from app.utils.logger import get_logger

logger = get_logger(__name__)


def detect_language(text: str) -> str:
    """Detect whether user text is Hindi or English.

    Args:
        text: User-provided text to inspect.

    Returns:
        ``"hi"`` for Hindi input, otherwise ``"en"``.

    Raises:
        ValueError: When the provided text is invalid.

    Example:
        >>> detect_language("Namaste dosto")
        'en'
    """
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    if not text.strip():
        return "en"
    try:
        lang = detect(text)
        return "hi" if lang == "hi" else "en"
    except Exception as error:
        logger.warning("Language detection failed: %s", error)
        return "en"


def translate_to_english(text: str) -> str:
    """Translate text into English.

    Args:
        text: Source text in any language.

    Returns:
        English translation when available, otherwise the original text.

    Raises:
        ValueError: When the provided text is invalid.

    Example:
        >>> translate_to_english("मतदान केंद्र कहाँ है")
        'Where is the polling booth'
    """
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    if not text.strip():
        return text
    try:
        return GoogleTranslator(source="auto", target="en").translate(text)
    except Exception as error:
        logger.warning("English translation failed: %s", error)
        return text


def translate_to_hindi(text: str) -> str:
    """Translate text into Hindi.

    Args:
        text: Source text in any language.

    Returns:
        Hindi translation when available, otherwise the original text.

    Raises:
        ValueError: When the provided text is invalid.

    Example:
        >>> translate_to_hindi("Where is my booth?")
        'मेरा बूथ कहाँ है?'
    """
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    if not text.strip():
        return text
    try:
        return GoogleTranslator(source="auto", target="hi").translate(text)
    except Exception as error:
        logger.warning("Hindi translation failed: %s", error)
        return text


def translate_to(text: str, target: str) -> str:
    """Translate text into the requested target language.

    Args:
        text: Source text in any language.
        target: Target language code such as ``"en"`` or ``"hi"``.

    Returns:
        Translated text when available, otherwise the original text.

    Raises:
        ValueError: When input arguments are invalid.

    Example:
        >>> translate_to("Vote dena zaroori hai", "en")
        'Voting is important'
    """
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    if not isinstance(target, str) or not target.strip():
        raise ValueError("Target language must be a non-empty string.")
    if not text.strip():
        return text
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception as error:
        logger.warning("Translation to %s failed: %s", target, error)
        return text
