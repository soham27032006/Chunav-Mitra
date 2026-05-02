from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    gemini_api_key: str
    grok_api_key: str = ""
    google_maps_api_key: str = ""
    google_translate_api_key: str = ""
    firebase_project_id: str
    firebase_service_account_path: str = "./firebase-service-account.json"
    app_env: str = "development"
    app_port: int = 8000
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:4173,http://127.0.0.1:4173,http://localhost:8080,http://127.0.0.1:8080"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
