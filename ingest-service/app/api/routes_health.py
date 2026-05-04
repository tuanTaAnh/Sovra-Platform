from fastapi import APIRouter

from app.clients.milvus_store import MilvusStore
from app.clients.ollama_client import OllamaClient
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    ollama = OllamaClient(settings.ollama_base_url)
    store = MilvusStore(settings.milvus_host, settings.milvus_port, settings.milvus_collection)
    return {
        "service": "ingest-service",
        "status": "ok",
        "ollama": "online" if ollama.health() else "offline",
        "milvus": "online" if store.health() else "offline",
        "embedding_model": settings.embedding_model,
        "docs_path": settings.docs_path,
        "collection": settings.milvus_collection,
    }