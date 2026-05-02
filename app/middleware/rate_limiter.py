"""
Module: rate_limiter.py
Description: Simple in-memory rate limiting middleware for Chunav Mitra.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.utils.logger import get_logger

logger = get_logger(__name__)

_rate_limit_storage: dict[str, list[float]] = {}
MAX_REQUESTS_PER_MINUTE = 30
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate-limit requests using a sliding-window algorithm."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Process a request while enforcing rate limits.

        Args:
            request: Incoming request object.
            call_next: Downstream request handler.

        Returns:
            HTTP response or rate-limit JSON error response.
        """
        client_ip = self._get_client_ip(request)
        is_allowed, retry_after = self._check_rate_limit(client_ip)

        if not is_allowed:
            logger.warning("Rate limit exceeded for IP %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message_hi": "Arey bhai, thoda ruk jaiye. 1 minute baad phir try kariye.",
                    "message_en": "Please slow down and try again in about a minute.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract the client IP address from proxy headers or socket info."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    def _check_rate_limit(self, client_ip: str) -> tuple[bool, int]:
        """Check whether a client is within the allowed rate limit."""
        current_time = time.time()
        timestamps = _rate_limit_storage.setdefault(client_ip, [])
        cutoff_time = current_time - WINDOW_SECONDS
        _rate_limit_storage[client_ip] = [timestamp for timestamp in timestamps if timestamp > cutoff_time]

        if len(_rate_limit_storage[client_ip]) < MAX_REQUESTS_PER_MINUTE:
            _rate_limit_storage[client_ip].append(current_time)
            return True, 0

        oldest_timestamp = min(_rate_limit_storage[client_ip])
        retry_after = max(int(oldest_timestamp + WINDOW_SECONDS - current_time) + 1, 1)
        return False, retry_after


def get_rate_limit_status(client_ip: str) -> dict[str, int]:
    """Return current rate-limit status metadata for a client IP."""
    current_time = time.time()
    timestamps = _rate_limit_storage.get(client_ip, [])
    cutoff_time = current_time - WINDOW_SECONDS
    valid_timestamps = [timestamp for timestamp in timestamps if timestamp > cutoff_time]
    remaining = max(0, MAX_REQUESTS_PER_MINUTE - len(valid_timestamps))
    reset = int(min(valid_timestamps) + WINDOW_SECONDS) if valid_timestamps else int(current_time + WINDOW_SECONDS)
    return {
        "limit": MAX_REQUESTS_PER_MINUTE,
        "remaining": remaining,
        "reset": reset,
    }
