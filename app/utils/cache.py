"""
Module: cache.py
Description: In-memory cache utilities for Chunav Mitra API responses.
Author: Chunav Mitra Team
Version: 1.0.0
"""

from __future__ import annotations

from datetime import datetime, timedelta
import hashlib
import json
from threading import Lock
from typing import Any


class SimpleCache:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self) -> None:
        """Initialize the cache store."""
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._lock = Lock()

    def make_key(self, *args: Any) -> str:
        """Generate a cache key from arguments.

        Args:
            *args: Values to hash into a cache key.

        Returns:
            A deterministic cache key string.
        """
        content = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Any | None:
        """Get a cached value if it exists and is not expired.

        Args:
            key: Cache key to resolve.

        Returns:
            The cached value when present and fresh, otherwise ``None``.
        """
        with self._lock:
            if key not in self._cache:
                return None
            value, expires_at = self._cache[key]
            if datetime.now() >= expires_at:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Store a value with a TTL.

        Args:
            key: Cache key to store.
            value: Value to cache.
            ttl_seconds: Cache lifetime in seconds.
        """
        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[key] = (value, expires_at)

    def clear_expired(self) -> None:
        """Remove expired entries from the cache."""
        now = datetime.now()
        with self._lock:
            self._cache = {
                cache_key: cache_value
                for cache_key, cache_value in self._cache.items()
                if cache_value[1] > now
            }


cache = SimpleCache()
