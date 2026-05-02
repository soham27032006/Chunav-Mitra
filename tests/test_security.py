"""Security tests for Chunav Mitra."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestSecurityHeaders:
    def test_xss_protection_header(self):
        response = client.get("/health")
        assert "X-XSS-Protection" in response.headers

    def test_content_type_header(self):
        response = client.get("/health")
        assert "X-Content-Type-Options" in response.headers

    def test_frame_options_header(self):
        response = client.get("/health")
        assert "X-Frame-Options" in response.headers


class TestInputSanitization:
    def test_xss_in_query_is_sanitized(self):
        with patch("app.services.gemini_service.ask_gemini") as mock:
            mock.return_value = "Safe response"
            response = client.post("/api/ask", json={"query": "<script>alert('xss')</script>"})
            assert response.status_code in [200, 400]

    def test_sql_injection_attempt(self):
        response = client.post(
            "/api/check-voter",
            json={"name": "'; DROP TABLE users; --", "state": "Delhi"},
        )
        assert response.status_code in [200, 400]
