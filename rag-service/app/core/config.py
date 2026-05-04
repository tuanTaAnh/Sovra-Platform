from pydantic import BaseModel
import os


class Settings(BaseModel):
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    llm_model: str = os.getenv("LLM_MODEL", "llama3")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "bge-m3")
    milvus_host: str = os.getenv("MILVUS_HOST", "milvus")
    milvus_port: str = os.getenv("MILVUS_PORT", "19530")
    milvus_collection: str = os.getenv("MILVUS_COLLECTION", "sovra_knowledge_base")
    default_top_k: int = int(os.getenv("DEFAULT_TOP_K", "4"))


settings = Settings()