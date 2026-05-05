from typing import Literal

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services.rag_pipeline import RagPipeline


router = APIRouter(prefix="/rag", tags=["rag"])
pipeline = RagPipeline()


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(4, ge=1, le=20)
    chat_history: list[ChatHistoryItem] = Field(default_factory=list)


@router.post("/query")
def query_rag(request: QueryRequest):
    try:
        return pipeline.query(
            question=request.query,
            top_k=request.top_k,
            chat_history=[
                item.model_dump()
                for item in request.chat_history
            ],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
