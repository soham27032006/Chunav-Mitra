"""
Module: test_middleware.py
Purpose: Tests for rate limiter and security headers middleware.
Author: Chunav Mitra Team
Version: 2.0.0
"""

import pytest


class TestRateLimiter:
    """Tests for in-memory rate-limiting middleware."""

    def test_rate_limit_allows_normal_requests(self, client) -> None:
        """Normal single request must be allowed through."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_rate_limit_returns_valid_status(self, client) -> None:
        """Response is either 200 (allowed) or 429 (throttled)."""
        response = client.get("/health")
        assert response.status_code in [200, 429]

    def test_multiple_sequential_requests_allowed(self, client) -> None:
        """Five consecutive requests within limit must all return 200."""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200


class TestSecurityHeaders:
    """Verify all required security headers are present on every response."""

    def test_xss_protection_header(self, client) -> None:
        """XSS protection header must be set to block mode."""
        response = client.get("/health")
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_content_type_options_header(self, client) -> None:
        """Content-type sniffing must be disabled."""
        response = client.get("/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_frame_options_header(self, client) -> None:
        """Clickjacking protection must deny all frame embedding."""
        response = client.get("/health")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_referrer_policy_header(self, client) -> None:
        """Referrer policy must be explicitly set."""
        response = client.get("/health")
        assert "Referrer-Policy" in response.headers

    def test_permissions_policy_header(self, client) -> None:
        """Permissions policy must be explicitly set."""
        response = client.get("/health")
        assert "Permissions-Policy" in response.headers
        policy = response.headers["Permissions-Policy"]
        assert "microphone" in policy
        assert "camera" in policy

    def test_hsts_header(self, client) -> None:
        """HSTS header must be present with a max-age value."""
        response = client.get("/health")
        hsts = response.headers.get("Strict-Transport-Security", "")
        assert "max-age" in hsts

    def test_security_headers_on_post_endpoints(self, client) -> None:
        """Security headers must also be present on POST responses."""
        from unittest.mock import patch
        with patch("app.services.gemini_service.ask_gemini", return_value="ok"):
            response = client.post("/api/ask", json={"query": "Hello"})
        assert "X-Content-Type-Options" in response.headers

    def test_process_time_header_present(self, client) -> None:
        """X-Process-Time header must be injected by the timing middleware."""
        response = client.get("/health")
        assert "X-Process-Time" in response.headers
