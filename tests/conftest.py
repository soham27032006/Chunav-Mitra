"""Test configuration and shared fixtures for Chunav Mitra."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """Create test client with mocked external services."""
    with patch("app.services.firebase_service.save_message"), \
         patch("app.services.firebase_service.get_history", return_value=[]), \
         patch("app.services.firebase_service.log_query"), \
         patch("app.services.firebase_service.create_session",
               return_value="test-session-123"):
        from main import app
        yield TestClient(app)

@pytest.fixture
def mock_gemini():
    """Mock Gemini AI responses."""
    with patch("app.services.gemini_service.ask_gemini") as mock:
        mock.return_value = (
            "Bilkul! Polling booth yaani aapka Mandap hai — "
            "jahan asli kaam hota hai! 🏛️"
        )
        yield mock
