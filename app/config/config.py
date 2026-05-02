"""
Module: config.py
Purpose: Application configuration via pydantic-settings for Chunav Mitra.
         Loads environment variables from .env file and validates them at startup.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "get_settings"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All fields map directly to environment variable names (case-insensitive).
    Sensitive values such as API keys must be set in ``.env`` or the host
    environment and are **never** committed to version control.

    Attributes:
        gemini_api_key: Google Gemini AI API key for language generation.
        grok_api_key: Optional Grok API key (unused by default).
        google_maps_api_key: Optional Google Maps API key for geocoding.
        google_translate_api_key: Optional Google Translate API key.
        firebase_project_id: Firebase project identifier for Firestore.
        firebase_service_account_path: Path to the service-account JSON file.
        app_env: Deployment environment label (e.g. ``"production"``).
        app_port: TCP port on which uvicorn listens.
        allowed_origins: Comma-separated CORS origins.
        allowed_origin_regex: Regex pattern for dynamic CORS origin matching.
    """

    gemini_api_key: str
    grok_api_key: str = ""
    google_maps_api_key: str = ""
    google_translate_api_key: str = ""
    firebase_project_id: str
    firebase_service_account_path: str = "./firebase-service-account.json"
    app_env: str = "development"
    app_port: int = 8000
    allowed_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:4173,http://127.0.0.1:4173,"
        "http://localhost:8080,http://127.0.0.1:8080,"
        "https://chunav-mitra-frontend.onrender.com"
    )
    allowed_origin_regex: str = r"^https://.*\.onrender\.com$"

    @property
    def origins_list(self) -> list[str]:
        """Return allowed origins as a list.

        Returns:
            List of allowed CORS origin strings parsed from ``allowed_origins``.

        Example:
            >>> settings = Settings()
            >>> isinstance(settings.origins_list, list)
            True
        """
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Uses ``functools.lru_cache`` so the environment is only parsed once
    per process lifetime.

    Returns:
        Validated ``Settings`` instance loaded from the environment.

    Example:
        >>> settings = get_settings()
        >>> isinstance(settings.app_port, int)
        True
    """
    return Settings()
