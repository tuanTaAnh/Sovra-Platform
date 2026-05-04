from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ingest_pipeline import IngestPipeline

router = APIRouter(prefix="/ingest", tags=["ingest"])
pipeline = IngestPipeline()


class IngestRequest(BaseModel):
    reindex: bool = False


@router.post("/run")
def run_ingest(request: IngestRequest):
    try:
        return pipeline.run(reindex=request.reindex)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/stats")
def ingest_stats():
    try:
        return pipeline.store.stats()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc