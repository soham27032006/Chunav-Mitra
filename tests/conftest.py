"""
Module: conftest.py
Purpose: Shared pytest fixtures for Chunav Mitra tests.
         Provides a TestClient with mocked external services
         and resets the in-memory rate-limit store before each test.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

import app.middleware.rate_limiter as rate_limiter_module


@pytest.fixture(autouse=True)
def reset_rate_limiter() -> None:
    """Clear the in-memory rate-limit store before every test.

    Prevents rate-limit state from leaking between tests and causing
    false 429 responses in test suites that make many requests.

    Yields:
        None (autouse fixture, no explicit ``yield`` value needed).
    """
    rate_limiter_module._rate_limit_storage.clear()


@pytest.fixture
def client():
    """Create a FastAPI TestClient with all external services mocked.

    Patches Firebase ``save_message``, ``get_history``, ``log_query``, and
    ``create_session`` so that tests run without any real cloud connectivity.

    Yields:
        ``TestClient`` instance for the Chunav Mitra FastAPI app.

    Example:
        >>> def test_health(client):
        ...     assert client.get("/health").status_code == 200
    """
    with (
        patch("app.services.firebase_service.save_message"),
        patch("app.services.firebase_service.get_history", return_value=[]),
        patch("app.services.firebase_service.log_query"),
        patch(
            "app.services.firebase_service.create_session",
            return_value="test-session-123",
        ),
    ):
        from main import app
        yield TestClient(app)


@pytest.fixture
def mock_gemini():
    """Mock Gemini AI responses to return a deterministic answer.

    Yields:
        ``unittest.mock.MagicMock`` wrapping ``ask_gemini``.

    Example:
        >>> def test_ask(client, mock_gemini):
        ...     response = client.post("/api/ask", json={"query": "hello"})
        ...     assert response.status_code == 200
    """
    with patch("app.services.gemini_service.ask_gemini") as mock:
        mock.return_value = (
            "Bilkul! Polling booth yaani aapka Mandap hai — "
            "jahan asli kaam hota hai! 🏛️"
        )
        yield mock
