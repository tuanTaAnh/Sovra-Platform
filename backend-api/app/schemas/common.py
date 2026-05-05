from pydantic import BaseModel, Field
from typing import Any


class ServiceHealth(BaseModel):
    name: str
    ok: bool
    url: str | None = None
    status_code: int | None = None
    detail: Any | None = None


class ServicesHealthResponse(BaseModel):
    backend: ServiceHealth
    rag_service: ServiceHealth
    ingest_service: ServiceHealth


class ErrorResponse(BaseModel):
    detail: str
