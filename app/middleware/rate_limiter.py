"""
Module: rate_limiter.py
Purpose: Sliding-window in-memory rate limiting middleware for Chunav Mitra.
         Enforces a per-IP request quota of 30 requests per 60-second window
         and returns RFC-compliant 429 responses with Retry-After headers.
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

__all__ = ["RateLimitMiddleware", "get_rate_limit_status"]

_rate_limit_storage: dict[str, list[float]] = {}
MAX_REQUESTS_PER_MINUTE = 30
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate-limit requests using a sliding-window algorithm."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Enforce rate limits and forward accepted requests downstream.

        Uses the client's real IP (resolved through X-Forwarded-For) as the
        bucket key. Rejected requests immediately receive a 429 response with
        a ``Retry-After`` header indicating how many seconds to wait.

        Args:
            request: Incoming Starlette request object.
            call_next: Next middleware or route handler in the chain.

        Returns:
            Normal downstream response for accepted requests, or a JSON 429
            response for rate-limited clients.
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
        """Extract the originating client IP from request headers or socket.

        Checks ``X-Forwarded-For`` first (for reverse-proxy deployments),
        then ``X-Real-IP``, and finally falls back to the socket host.

        Args:
            request: Incoming Starlette request object.

        Returns:
            Client IP address string, or ``"unknown"`` when not determinable.

        Example:
            >>> middleware = RateLimitMiddleware(app=None)
        """
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
        """Check whether a client IP is within the sliding-window rate limit.

        Purges timestamps older than ``WINDOW_SECONDS`` before evaluating
        the limit, so the window is always computed from the current time.

        Args:
            client_ip: Originating client IP address string.

        Returns:
            A two-tuple of ``(is_allowed, retry_after_seconds)``.
            ``is_allowed`` is ``True`` when under the limit; ``retry_after_seconds``
            is 0 when allowed, otherwise the number of seconds to wait.

        Example:
            >>> middleware = RateLimitMiddleware(app=None)
            >>> allowed, wait = middleware._check_rate_limit("127.0.0.1")
            >>> allowed
            True
        """
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
    """Return the current rate-limit counters for a given client IP.

    Used for health-check dashboards or debug endpoints. Does **not**
    modify the rate-limit storage — it is purely read-only.

    Args:
        client_ip: Client IP address to inspect.

    Returns:
        Dictionary with ``limit`` (total allowed), ``remaining`` (requests left),
        and ``reset`` (Unix timestamp when the window resets).

    Example:
        >>> status = get_rate_limit_status("127.0.0.1")
        >>> "limit" in status and "remaining" in status
        True
    """
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
