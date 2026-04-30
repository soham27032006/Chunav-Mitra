import firebase_admin
from firebase_admin import credentials, firestore
from app.config import get_settings
from datetime import datetime
import uuid

settings = get_settings()

def _init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_service_account_path)
        firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})

_init_firebase()
db = firestore.client()

def create_session() -> str:
    return str(uuid.uuid4())

def save_message(session_id: str, role: str, content: str, user_id: str = None):
    """Save one chat turn to Firestore"""
    db.collection("sessions").document(session_id)\
      .collection("messages").add({
          "role": role,          # "user" | "model"
          "content": content,
          "user_id": user_id,
          "timestamp": datetime.utcnow(),
      })

def get_history(session_id: str, limit: int = 8) -> list:
    """
    Fetch last N messages formatted for Gemini chat history.
    Gemini expects: [{"role": "user"|"model", "parts": ["text"]}]
    """
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
    return list(reversed(history))  # oldest first for Gemini

def log_query(session_id: str, intent: str, lang: str):
    """Analytics: log each query intent for insights"""
    db.collection("analytics").add({
        "session_id": session_id,
        "intent": intent,
        "lang": lang,
        "timestamp": datetime.utcnow(),
    })
