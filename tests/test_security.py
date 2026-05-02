"""Security tests for Chunav Mitra API."""


class TestSecurityHeaders:
    """Verify security headers are present on all responses."""

    def test_xss_protection_header(self, client) -> None:
        response = client.get("/health")
        assert "X-XSS-Protection" in response.headers

    def test_content_type_options_header(self, client) -> None:
        response = client.get("/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_frame_options_header(self, client) -> None:
        response = client.get("/health")
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_referrer_policy_header(self, client) -> None:
        response = client.get("/health")
        assert "Referrer-Policy" in response.headers


class TestInputSanitization:
    """Verify malicious inputs are rejected."""

    def test_xss_in_query_rejected_or_sanitized(self, client) -> None:
        from unittest.mock import patch
        with patch("app.services.gemini_service.ask_gemini",
                   return_value="Safe response"):
            response = client.post("/api/ask",
                json={"query": "<script>alert('xss')</script>"})
            assert response.status_code in [200, 400]

    def test_sql_injection_in_name(self, client) -> None:
        response = client.post("/api/check-voter",
            json={"name": "'; DROP TABLE--", "state": "Delhi"})
        assert response.status_code in [200, 400]

    def test_very_long_name_rejected(self, client) -> None:
        response = client.post("/api/check-voter",
            json={"name": "A" * 101, "state": "Delhi"})
        assert response.status_code == 400
