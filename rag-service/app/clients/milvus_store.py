from __future__ import annotations

import os
from time import perf_counter
from typing import Any

from pymilvus import MilvusClient


def elapsed_ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 2)


class MilvusStore:
    """
    Milvus Lite store for RAG retrieval.

    This version uses a local Milvus Lite database file instead of connecting
    to a standalone Milvus server by host/port.

    Example:
        MILVUS_DB_PATH=/app/data/sovra_milvus.db
        MILVUS_COLLECTION=sovra_knowledge_base
    """

    def __init__(
        self,
        collection_name: str,
        db_path: str | None = None,
        host: str | None = None,
        port: str | None = None,
    ):
        self.collection_name = collection_name

        # host and port are kept only for backward compatibility with old callers.
        # They are not used in Milvus Lite mode.
        self.host = host
        self.port = port

        self.db_path = db_path or os.getenv("MILVUS_DB_PATH", "/app/data/sovra_milvus.db")
        self._client: MilvusClient | None = None

    def connect(self) -> None:
        if self._client is not None:
            return

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._client = MilvusClient(uri=self.db_path)

    @property
    def client(self) -> MilvusClient:
        self.connect()

        if self._client is None:
            raise RuntimeError("Milvus Lite client was not initialized")

        return self._client

    def health(self) -> bool:
        try:
            self.connect()
            self.client.list_collections()
            return True
        except Exception:
            return False

    def search(self, query_vector: list[float], top_k: int = 4) -> list[dict[str, Any]]:
        hits, _ = self.search_with_timing(query_vector=query_vector, top_k=top_k)
        return hits

    def search_with_timing(
        self,
        query_vector: list[float],
        top_k: int = 4,
    ) -> tuple[list[dict[str, Any]], dict[str, float]]:
        timings: dict[str, float] = {}
        total_start = perf_counter()

        connect_start = perf_counter()
        self.connect()
        timings["connect_ms"] = elapsed_ms(connect_start)

        collection_check_start = perf_counter()
        collection_exists = self.client.has_collection(
            collection_name=self.collection_name
        )
        timings["collection_check_ms"] = elapsed_ms(collection_check_start)

        if not collection_exists:
            timings["collection_load_ms"] = 0.0
            timings["vector_search_ms"] = 0.0
            timings["format_results_ms"] = 0.0
            timings["total_ms"] = elapsed_ms(total_start)
            return [], timings

        # Milvus Lite with MilvusClient does not need Collection(...).load()
        # in the same way as the old ORM-style API.
        timings["collection_load_ms"] = 0.0

        search_start = perf_counter()
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=["text", "source", "doc_type"],
            search_params={
                "metric_type": "COSINE",
                "params": {},
            },
        )
        timings["vector_search_ms"] = elapsed_ms(search_start)

        format_start = perf_counter()
        hits: list[dict[str, Any]] = []

        for hit in results[0]:
            entity = hit.get("entity", {})

            hits.append(
                {
                    "score": float(hit.get("distance", 0.0)),
                    "text": entity.get("text"),
                    "source": entity.get("source"),
                    "doc_type": entity.get("doc_type"),
                }
            )

        timings["format_results_ms"] = elapsed_ms(format_start)
        timings["total_ms"] = elapsed_ms(total_start)

        return hits, timings