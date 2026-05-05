from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / "infra" / "env" / ".env"


class Settings(BaseSettings):
    app_version: str = "local"
    environment: str = "local"

    ollama_base_url: str = "http://localhost:11434"
    embedding_model: str = "all-minilm"

    milvus_host: str = "localhost"
    milvus_port: str = "19530"
    milvus_collection: str = "sovra_knowledge_base"

    docs_path: str = str(PROJECT_ROOT / "data" / "docs")
    chunk_size: int = 500
    chunk_overlap: int = 100

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()