from __future__ import annotations

import os
import time
from typing import Any

from pymilvus import DataType, MilvusClient


class MilvusStore:
    """
    Milvus Lite store for document ingestion.

    This replaces Milvus Standalone host/port connection with a local
    Milvus Lite database file.

    Old mode:
        MILVUS_HOST=milvus
        MILVUS_PORT=19530

    New mode:
        MILVUS_DB_PATH=/app/milvus/sovra_milvus.db
    """

    def __init__(
        self,
        host: str | None = None,
        port: str | None = None,
        collection_name: str | None = None,
        db_path: str | None = None,
    ):
        # host and port are kept for backward compatibility with old callers.
        # They are not used in Milvus Lite mode.
        self.host = host
        self.port = port

        self.collection_name = collection_name or os.getenv(
            "MILVUS_COLLECTION",
            "sovra_knowledge_base",
        )

        self.db_path = db_path or os.getenv(
            "MILVUS_DB_PATH",
            "/app/milvus/sovra_milvus.db",
        )

        self._client: MilvusClient | None = None

    def connect(self, retries: int = 20, delay_seconds: float = 2.0) -> None:
        if self._client is not None:
            return

        last_error: Exception | None = None

        for _ in range(retries):
            try:
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                self._client = MilvusClient(uri=self.db_path)
                self._client.list_collections()
                return
            except Exception as exc:
                last_error = exc
                time.sleep(delay_seconds)

        raise RuntimeError(
            f"Could not connect to Milvus Lite at {self.db_path}: {last_error}"
        )

    @property
    def client(self) -> MilvusClient:
        self.connect()

        if self._client is None:
            raise RuntimeError("Milvus Lite client was not initialized")

        return self._client

    def health(self) -> bool:
        try:
            self.connect(retries=1, delay_seconds=0.1)
            self.client.list_collections()
            return True
        except Exception:
            return False

    def recreate_collection(self, dim: int) -> str:
        self.connect()

        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)

        self.create_collection(dim)
        return self.collection_name

    def create_collection(self, dim: int) -> str:
        self.connect()

        if self.client.has_collection(collection_name=self.collection_name):
            return self.collection_name

        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=False,
        )

        schema.add_field(
            field_name="id",
            datatype=DataType.INT64,
            is_primary=True,
        )
        schema.add_field(
            field_name="vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=dim,
        )
        schema.add_field(
            field_name="text",
            datatype=DataType.VARCHAR,
            max_length=8192,
        )
        schema.add_field(
            field_name="source",
            datatype=DataType.VARCHAR,
            max_length=512,
        )
        schema.add_field(
            field_name="doc_type",
            datatype=DataType.VARCHAR,
            max_length=128,
        )

        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )

        return self.collection_name

    def insert_chunks(
        self,
        vectors: list[list[float]],
        texts: list[str],
        sources: list[str],
        doc_types: list[str],
    ) -> int:
        if not vectors:
            return 0

        self.create_collection(dim=len(vectors[0]))

        rows: list[dict[str, Any]] = []

        for vector, text, source, doc_type in zip(vectors, texts, sources, doc_types):
            rows.append(
                {
                    "vector": vector,
                    "text": text,
                    "source": source,
                    "doc_type": doc_type,
                }
            )

        self.client.insert(
            collection_name=self.collection_name,
            data=rows,
        )

        return len(rows)

    def stats(self) -> dict:
        self.connect()

        if not self.client.has_collection(collection_name=self.collection_name):
            return {
                "collection": self.collection_name,
                "exists": False,
                "entities": 0,
                "milvus_db_path": self.db_path,
            }

        stats = self.client.get_collection_stats(
            collection_name=self.collection_name,
        )

        row_count = stats.get("row_count", 0)

        return {
            "collection": self.collection_name,
            "exists": True,
            "entities": int(row_count),
            "milvus_db_path": self.db_path,
        }