from pydantic import BaseModel, Field
from typing import Any, Literal


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=1, ge=1, le=20)
    conversation_id: str | None = None
    save_history: bool = True


class SourceItem(BaseModel):
    source: str | None = None
    doc_type: str | None = None
    score: float | None = None
    preview: str | None = None


class ChatQueryResponse(BaseModel):
    conversation_id: str | None = None
    answer: str
    sources: list[dict[str, Any]] = []
    retrieval_used: bool = False
    llm_model: str | None = None
    embedding_model: str | None = None
    collection: str | None = None
    mode: str | None = None
    cloud_api_required: bool | None = None
    timings_ms: dict[str, Any] | None = None


class CreateConversationRequest(BaseModel):
    title: str | None = None


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ChatMessage(BaseModel):
    id: str
    conversation_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    sources: list[dict[str, Any]] = []
    timings_ms: dict[str, Any] | None = None
    created_at: str


class ConversationDetail(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[ChatMessage]
