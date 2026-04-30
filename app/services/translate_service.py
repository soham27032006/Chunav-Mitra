"""Google Translate service for Hindi ↔ English translation."""
from google.cloud import translate_v2 as translate
from app.config import get_settings
import re

settings = get_settings()

# Initialize Translate client
try:
    translate_client = translate.Client()
except Exception:
    # Fallback: create without explicit credentials (uses env var)
    translate_client = None


def detect_language(text: str) -> str:
    """
    Detect if text is Hindi or English.
    Returns: "hi" for Hindi, "en" for English.
    """
    if not text:
        return "en"

    # Count Hindi Unicode characters (Devanagari range: 0900-097F)
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    total_chars = len(re.findall(r'\w', text))

    # If more than 30% Hindi characters, consider it Hindi
    if total_chars > 0 and hindi_chars / total_chars > 0.3:
        return "hi"

    # Check for common Hindi words
    hindi_words = ["क्या", "है", "का", "की", "के", "में", "से", "को", "और",
                   "एक", "हैं", "यह", "वह", "मैं", "आप", "हम", "ने", "भी"]
    text_lower = text.lower()
    word_count = sum(1 for word in hindi_words if word in text_lower)

    if word_count >= 2:
        return "hi"

    return "en"


def translate_to_english(text: str) -> str:
    """Translate Hindi text to English."""
    if not text or not translate_client:
        return text

    try:
        result = translate_client.translate(text, target_language="en")
        return result["translatedText"]
    except Exception:
        return text


def translate_to_hindi(text: str) -> str:
    """Translate English text to Hindi."""
    if not text or not translate_client:
        return text

    try:
        result = translate_client.translate(text, target_language="hi")
        return result["translatedText"]
    except Exception:
        return text
