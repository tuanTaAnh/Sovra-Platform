from fastapi import APIRouter

from app.clients.ollama_client import OllamaClient
from app.clients.milvus_store import MilvusStore
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    ollama = OllamaClient(settings.ollama_base_url)

    store = MilvusStore(
        collection_name=settings.milvus_collection,
        db_path=settings.milvus_db_path,
    )

    return {
        "service": "rag-service",
        "status": "ok",
        "ollama": "online" if ollama.health() else "offline",
        "milvus": "online" if store.health() else "offline",
        "collection": settings.milvus_collection,
        "milvus_db_path": settings.milvus_db_path,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
    }