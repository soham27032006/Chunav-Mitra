"""
Module: security_headers.py
Purpose: Security-hardening HTTP response headers middleware for Chunav Mitra.
         Injects the full suite of OWASP-recommended defensive headers on
         every response including 429 rate-limit rejections.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

__all__ = ["SecurityHeadersMiddleware", "SECURITY_HEADERS"]

# ── Default security headers applied to every response ───────────────────────
SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(self), microphone=(self), camera=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Permitted-Cross-Domain-Policies": "none",
}
"""Mapping of HTTP security header names to their enforced values."""


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject OWASP-recommended security headers on every HTTP response.

    Applies a fixed set of defensive headers to prevent cross-site scripting,
    clickjacking, MIME-type sniffing, and information leakage. The headers are
    also applied to non-2xx responses such as 429 rate-limit replies.

    Attributes:
        headers: Dictionary of header name-value pairs to inject.
    """

    def __init__(self, app, headers: dict[str, str] | None = None) -> None:
        """Initialise the middleware with a configurable header dictionary.

        Args:
            app: The ASGI application to wrap.
            headers: Optional override mapping; defaults to ``SECURITY_HEADERS``.

        Example:
            >>> from fastapi import FastAPI
            >>> app = FastAPI()
            >>> app.add_middleware(SecurityHeadersMiddleware)
        """
        super().__init__(app)
        self.headers = headers if headers is not None else SECURITY_HEADERS

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Inject security headers into every downstream response.

        Calls the next middleware or route handler and then unconditionally
        sets all configured security headers on the resulting response object,
        regardless of the HTTP status code.

        Args:
            request: Incoming Starlette request object.
            call_next: Callable that invokes the next ASGI layer.

        Returns:
            The response with all security headers applied.

        Example:
            A GET /health response will include:
            ``X-Content-Type-Options: nosniff``
            ``X-Frame-Options: DENY``
            ``Strict-Transport-Security: max-age=31536000; includeSubDomains``
        """
        response = await call_next(request)
        for header_name, header_value in self.headers.items():
            response.headers[header_name] = header_value
        return response
