import firebase_admin
from firebase_admin import credentials, firestore
from app.config import get_settings
from datetime import datetime
import uuid
import os

settings = get_settings()

db = None

def _init_firebase():
    global db
    if not firebase_admin._apps:
        cert_path = settings.firebase_service_account_path
        if cert_path and os.path.exists(cert_path):
            try:
                cred = credentials.Certificate(cert_path)
                firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
                db = firestore.client()
            except Exception:
                # Firebase not available - run in mock mode
                pass

_init_firebase()

# In-memory storage for mock mode
_mock_messages = {}
_mock_analytics = []
_mock_sessions = set()

def create_session() -> str:
    session_id = str(uuid.uuid4())
    if not db:
        _mock_sessions.add(session_id)
    return session_id

def save_message(session_id: str, role: str, content: str, user_id: str = None):
    """Save one chat turn to Firestore (or mock if Firebase unavailable)"""
    if db:
        db.collection("sessions").document(session_id)\
          .collection("messages").add({
              "role": role,
              "content": content,
              "user_id": user_id,
              "timestamp": datetime.utcnow(),
          })
    else:
        if session_id not in _mock_messages:
            _mock_messages[session_id] = []
        _mock_messages[session_id].append({
            "role": role,
            "content": content,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
        })

def get_history(session_id: str, limit: int = 8) -> list:
    """
    Fetch last N messages formatted for Gemini chat history.
    Gemini expects: [{"role": "user"|"model", "parts": ["text"]}]
    """
    if db:
        docs = (
            db.collection("sessions").document(session_id)
              .collection("messages")
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
              .limit(limit)
              .stream()
        )
        history = [
            {"role": d.to_dict()["role"], "parts": [d.to_dict()["content"]]}
            for d in docs
        ]
        return list(reversed(history))
    else:
        # Mock mode - return from memory
        messages = _mock_messages.get(session_id, [])
        history = [
            {"role": m["role"], "parts": [m["content"]]}
            for m in messages[-limit:]
        ]
        return history

def log_query(session_id: str, intent: str, lang: str):
    """Analytics: log each query intent for insights"""
    if db:
        db.collection("analytics").add({
            "session_id": session_id,
            "intent": intent,
            "lang": lang,
            "timestamp": datetime.utcnow(),
        })
    else:
        _mock_analytics.append({
            "session_id": session_id,
            "intent": intent,
            "lang": lang,
            "timestamp": datetime.utcnow(),
        })
