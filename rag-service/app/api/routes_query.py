from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services.rag_pipeline import RagPipeline

router = APIRouter(prefix="/rag", tags=["rag"])
pipeline = RagPipeline()


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(4, ge=1, le=10)


@router.post("/query")
def query_rag(request: QueryRequest):
    try:
        return pipeline.query(request.query, top_k=request.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc