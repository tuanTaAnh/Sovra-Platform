from pydantic import BaseModel
import os


class Settings(BaseModel):
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "bge-m3")
    milvus_host: str = os.getenv("MILVUS_HOST", "milvus")
    milvus_port: str = os.getenv("MILVUS_PORT", "19530")
    milvus_collection: str = os.getenv("MILVUS_COLLECTION", "sovra_knowledge_base")
    docs_path: str = os.getenv("DOCS_PATH", "/app/data/docs")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))


settings = Settings()