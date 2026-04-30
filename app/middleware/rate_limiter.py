import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# In-memory rate limiter storage: {ip: [timestamps]}
_rate_limit_storage = {}
MAX_REQUESTS_PER_MINUTE = 30
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter middleware.
    Max 30 requests per minute per IP address.
    Uses sliding window algorithm.
    """

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit
        is_allowed, retry_after = self._check_rate_limit(client_ip)

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message_hi": "Arey bhai, thoda ruko! Shaadi mein bhi line lagti hai. 1 minute baad try karo.",
                    "message_en": "Easy there! Even wedding queues need patience. Try again in 1 minute.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )

        # Process the request
        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers or connection."""
        # Check for forwarded headers (if behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection IP
        if hasattr(request.client, 'host'):
            return request.client.host

        return "unknown"

    def _check_rate_limit(self, client_ip: str) -> tuple[bool, int]:
        """
        Check if request is within rate limit.
        Returns: (is_allowed: bool, retry_after: int)
        """
        current_time = time.time()

        # Get or create timestamp list for this IP
        if client_ip not in _rate_limit_storage:
            _rate_limit_storage[client_ip] = []

        timestamps = _rate_limit_storage[client_ip]

        # Remove timestamps older than the window
        cutoff_time = current_time - WINDOW_SECONDS
        _rate_limit_storage[client_ip] = [
            ts for ts in timestamps if ts > cutoff_time
        ]

        # Check if under limit
        if len(_rate_limit_storage[client_ip]) < MAX_REQUESTS_PER_MINUTE:
            # Add current timestamp and allow
            _rate_limit_storage[client_ip].append(current_time)
            return True, 0

        # Rate limit exceeded - calculate retry after
        oldest_timestamp = min(_rate_limit_storage[client_ip])
        retry_after = int(oldest_timestamp + WINDOW_SECONDS - current_time) + 1
        retry_after = max(retry_after, 1)  # At least 1 second

        return False, retry_after


def get_rate_limit_status(client_ip: str) -> dict:
    """
    Helper function to check current rate limit status for an IP.
    Returns info about remaining requests and reset time.
    """
    current_time = time.time()

    if client_ip not in _rate_limit_storage:
        return {
            "limit": MAX_REQUESTS_PER_MINUTE,
            "remaining": MAX_REQUESTS_PER_MINUTE,
            "reset": int(current_time + WINDOW_SECONDS)
        }

    timestamps = _rate_limit_storage[client_ip]
    cutoff_time = current_time - WINDOW_SECONDS

    # Clean old timestamps
    valid_timestamps = [ts for ts in timestamps if ts > cutoff_time]

    remaining = max(0, MAX_REQUESTS_PER_MINUTE - len(valid_timestamps))

    if valid_timestamps:
        reset_time = int(min(valid_timestamps) + WINDOW_SECONDS)
    else:
        reset_time = int(current_time + WINDOW_SECONDS)

    return {
        "limit": MAX_REQUESTS_PER_MINUTE,
        "remaining": remaining,
        "reset": reset_time
    }
