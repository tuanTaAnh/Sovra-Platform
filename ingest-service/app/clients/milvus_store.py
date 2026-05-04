from __future__ import annotations

import time

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)


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
        raise RuntimeError(f"Could not connect to Milvus at {self.host}:{self.port}: {last_error}")

    def health(self) -> bool:
        try:
            self.connect(retries=1, delay_seconds=0.1)
            utility.list_collections()
            return True
        except Exception:
            return False

    def recreate_collection(self, dim: int) -> Collection:
        self.connect()
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
        return self.create_collection(dim)

    def create_collection(self, dim: int) -> Collection:
        self.connect()
        if utility.has_collection(self.collection_name):
            collection = Collection(self.collection_name)
            collection.load()
            return collection

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=128),
        ]
        schema = CollectionSchema(fields=fields, description="Sovra AI private knowledge base")
        collection = Collection(self.collection_name, schema=schema)
        collection.create_index(
            field_name="vector",
            index_params={
                "index_type": "HNSW",
                "metric_type": "COSINE",
                "params": {"M": 8, "efConstruction": 64},
            },
        )
        collection.load()
        return collection

    def insert_chunks(
        self,
        vectors: list[list[float]],
        texts: list[str],
        sources: list[str],
        doc_types: list[str],
    ) -> int:
        if not vectors:
            return 0

        collection = self.create_collection(dim=len(vectors[0]))

        # Since id is auto_id=True, insert only non-primary fields in schema order.
        collection.insert([vectors, texts, sources, doc_types])
        collection.flush()
        collection.load()
        return len(vectors)

    def stats(self) -> dict:
        self.connect()
        if not utility.has_collection(self.collection_name):
            return {
                "collection": self.collection_name,
                "exists": False,
                "entities": 0,
            }

        collection = Collection(self.collection_name)
        collection.flush()
        return {
            "collection": self.collection_name,
            "exists": True,
            "entities": collection.num_entities,
        }