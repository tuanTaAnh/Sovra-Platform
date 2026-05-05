from fastapi import APIRouter

from app.clients.ingest_client import IngestClient
from app.core.config import get_settings
from app.schemas.ingest import IngestRunRequest


router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.get("/health")
async def ingest_health():
    settings = get_settings()
    return await IngestClient(settings).health()


@router.get("/stats")
async def ingest_stats():
    settings = get_settings()
    return await IngestClient(settings).stats()


@router.post("/run")
async def ingest_run(payload: IngestRunRequest):
    settings = get_settings()
    return await IngestClient(settings).run(reindex=payload.reindex)
