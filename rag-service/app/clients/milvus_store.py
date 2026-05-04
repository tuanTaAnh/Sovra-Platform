from __future__ import annotations

import time
from time import perf_counter
from typing import Any

from pymilvus import Collection, connections, utility


def elapsed_ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 2)


class MilvusStore:
    def __init__(self, host: str, port: str, collection_name: str):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self._connected = False

    def connect(self, retries: int = 20, delay_seconds: float = 2.0) -> None:
        if self._connected:
            return

        last_error: Exception | None = None

        for _ in range(retries):
            try:
                connections.connect(alias="default", host=self.host, port=self.port)
                utility.list_collections()
                self._connected = True
                return
            except Exception as exc:
                last_error = exc
                time.sleep(delay_seconds)

        raise RuntimeError(
            f"Could not connect to Milvus at {self.host}:{self.port}: {last_error}"
        )

    def health(self) -> bool:
        try:
            self.connect(retries=1, delay_seconds=0.1)
            utility.list_collections()
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
        collection_exists = utility.has_collection(self.collection_name)
        timings["collection_check_ms"] = elapsed_ms(collection_check_start)

        if not collection_exists:
            timings["collection_load_ms"] = 0.0
            timings["vector_search_ms"] = 0.0
            timings["format_results_ms"] = 0.0
            timings["total_ms"] = elapsed_ms(total_start)
            return [], timings

        load_start = perf_counter()
        collection = Collection(self.collection_name)
        collection.load()
        timings["collection_load_ms"] = elapsed_ms(load_start)

        search_start = perf_counter()
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param={
                "metric_type": "COSINE",
                "params": {"ef": 64},
            },
            limit=top_k,
            output_fields=["text", "source", "doc_type"],
        )
        timings["vector_search_ms"] = elapsed_ms(search_start)

        format_start = perf_counter()
        hits: list[dict[str, Any]] = []

        for hit in results[0]:
            entity = hit.entity
            hits.append(
                {
                    "score": float(hit.score),
                    "text": entity.get("text"),
                    "source": entity.get("source"),
                    "doc_type": entity.get("doc_type"),
                }
            )

        timings["format_results_ms"] = elapsed_ms(format_start)
        timings["total_ms"] = elapsed_ms(total_start)

        return hits, timings