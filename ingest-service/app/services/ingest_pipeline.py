from __future__ import annotations

from app.clients.milvus_store import MilvusStore
from app.clients.ollama_client import OllamaClient
from app.core.config import settings
from app.services.chunker import chunk_text
from app.services.document_loader import load_documents


class IngestPipeline:
    def __init__(self) -> None:
        self.ollama = OllamaClient(settings.ollama_base_url)
        self.store = MilvusStore(
            settings.milvus_host,
            settings.milvus_port,
            settings.milvus_collection,
        )

    def run(self, reindex: bool = False) -> dict:
        documents = load_documents(settings.docs_path)
        if not documents:
            return {
                "status": "completed",
                "documents_processed": 0,
                "chunks_indexed": 0,
                "message": f"No .md or .txt files found under {settings.docs_path}",
            }

        all_vectors: list[list[float]] = []
        all_texts: list[str] = []
        all_sources: list[str] = []
        all_doc_types: list[str] = []
        document_summaries: list[dict] = []

        for doc in documents:
            chunks = chunk_text(doc["text"], settings.chunk_size, settings.chunk_overlap)
            document_summaries.append(
                {
                    "source": doc["source"],
                    "doc_type": doc["doc_type"],
                    "chunks": len(chunks),
                }
            )

            for idx, chunk in enumerate(chunks):
                vector = self.ollama.embed(settings.embedding_model, chunk)
                all_vectors.append(vector)
                all_texts.append(chunk)
                all_sources.append(f"{doc['source']}#chunk-{idx + 1}")
                all_doc_types.append(doc["doc_type"])

        if reindex and all_vectors:
            self.store.recreate_collection(dim=len(all_vectors[0]))

        inserted = self.store.insert_chunks(
            all_vectors,
            all_texts,
            all_sources,
            all_doc_types,
        )

        stats = self.store.stats()

        return {
            "status": "completed",
            "documents_processed": len(documents),
            "chunks_indexed": inserted,
            "embedding_model": settings.embedding_model,
            "collection": settings.milvus_collection,
            "milvus_entities": stats.get("entities", 0),
            "documents": document_summaries,
        }
