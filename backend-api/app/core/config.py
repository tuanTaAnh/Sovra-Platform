from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / "infra" / "env" / ".env"


class Settings(BaseSettings):
    app_name: str = "Sovra Backend API"
    app_version: str = "local"
    environment: str = "local"

    api_v1_prefix: str = "/api/v1"

    backend_api_port: int = 8000

    rag_service_url: str = "http://localhost:8001"
    ingest_service_url: str = "http://localhost:8002"

    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

    database_url: str = "sqlite:///./backend_api.db"

    http_timeout_seconds: float = 180.0

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()