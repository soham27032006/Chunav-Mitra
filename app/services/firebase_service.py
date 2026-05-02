"""
Module: firebase_service.py
Description: Persistence and analytics helpers for Chunav Mitra.
Supports Firebase-backed storage with a safe in-memory fallback.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from datetime import UTC, datetime
import os
import uuid

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
db = None

_mock_messages: dict[str, list[dict[str, object]]] = {}
_mock_analytics: list[dict[str, object]] = []
_mock_sessions: set[str] = set()


def _init_firebase() -> None:
    """Initialize Firebase once when credentials are available.

    Args:
        None.

    Returns:
        None.

    Raises:
        RuntimeError: When Firebase initialization fails unexpectedly.

    Example:
        >>> _init_firebase()
    """
    global db
    if db is not None:
        return
    if firebase_admin._apps:
        db = firestore.client()
        return

    cert_path = settings.firebase_service_account_path
    if not cert_path or not os.path.exists(cert_path):
        logger.warning("Firebase credentials not found. Using mock storage mode.")
        return

    try:
        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
        db = firestore.client()
        logger.info("Firebase initialized successfully.")
    except Exception as error:
        logger.warning("Firebase initialization failed. Using mock mode. Error: %s", error)
        db = None


def _get_database_client():
    """Return an active Firebase client when available.

    Args:
        None.

    Returns:
        Firestore client instance or ``None`` when running in mock mode.

    Raises:
        RuntimeError: When Firebase cannot be initialized after a retry.

    Example:
        >>> client = _get_database_client()
    """
    global db
    if db is None:
        _init_firebase()
    return db


def create_session() -> str:
    """Create a unique session identifier.

    Args:
        None.

    Returns:
        A unique session id string.

    Raises:
        RuntimeError: When UUID generation fails.

    Example:
        >>> session_id = create_session()
        >>> isinstance(session_id, str)
        True
    """
    session_id = str(uuid.uuid4())
    if _get_database_client() is None:
        _mock_sessions.add(session_id)
    return session_id


def save_message(session_id: str, role: str, content: str, user_id: str | None = None) -> None:
    """Persist a chat message.

    Args:
        session_id: Conversation session id.
        role: Message role, such as ``user`` or ``model``.
        content: Message content.
        user_id: Optional user identifier.

    Returns:
        None.

    Raises:
        ValueError: When required values are missing.

    Example:
        >>> save_message("session-1", "user", "Hello")
    """
    if not session_id or not role or not content:
        raise ValueError("session_id, role, and content are required.")

    client = _get_database_client()
    record = {
        "role": role,
        "content": content,
        "user_id": user_id,
        "timestamp": datetime.now(UTC),
    }

    if client:
        client.collection("sessions").document(session_id).collection("messages").add(record)
        return

    _mock_messages.setdefault(session_id, []).append(record)


def get_history(session_id: str, limit: int = 8) -> list[dict[str, object]]:
    """Fetch recent chat history formatted for Gemini chat sessions.

    Args:
        session_id: Conversation session id.
        limit: Maximum number of messages to fetch.

    Returns:
        Chat history in Gemini-compatible role/parts format.

    Raises:
        ValueError: When the session id is invalid.

    Example:
        >>> get_history("session-1", limit=4)
        []
    """
    if not session_id:
        raise ValueError("session_id is required.")

    client = _get_database_client()
    if client:
        docs = (
            client.collection("sessions")
            .document(session_id)
            .collection("messages")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        history = [
            {"role": doc.to_dict()["role"], "parts": [doc.to_dict()["content"]]}
            for doc in docs
        ]
        return list(reversed(history))

    messages = _mock_messages.get(session_id, [])
    return [{"role": item["role"], "parts": [item["content"]]} for item in messages[-limit:]]


def log_query(session_id: str, intent: str, lang: str) -> None:
    """Store analytics metadata for a query.

    Args:
        session_id: Conversation session id.
        intent: Classified user intent.
        lang: Language code for the request.

    Returns:
        None.

    Raises:
        ValueError: When required values are missing.

    Example:
        >>> log_query("session-1", "general", "en")
    """
    if not session_id or not intent or not lang:
        raise ValueError("session_id, intent, and lang are required.")

    client = _get_database_client()
    record = {
        "session_id": session_id,
        "intent": intent,
        "lang": lang,
        "timestamp": datetime.now(UTC),
    }
    if client:
        client.collection("analytics").add(record)
        return

    _mock_analytics.append(record)


_init_firebase()
