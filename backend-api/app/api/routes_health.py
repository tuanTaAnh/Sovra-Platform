from fastapi import APIRouter

from app.clients.ingest_client import IngestClient
from app.clients.rag_client import RAGClient
from app.core.config import get_settings
from app.schemas.common import ServiceHealth, ServicesHealthResponse


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health():
    settings = get_settings()

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "ok": True,
    }


@router.get("/services", response_model=ServicesHealthResponse)
async def services_health():
    settings = get_settings()

    backend = ServiceHealth(
        name="backend-api",
        ok=True,
        url="self",
        detail={
            "version": settings.app_version,
            "environment": settings.environment,
        },
    )

    rag_status = ServiceHealth(
        name="rag-service",
        ok=False,
        url=settings.rag_service_url,
    )

    ingest_status = ServiceHealth(
        name="ingest-service",
        ok=False,
        url=settings.ingest_service_url,
    )

    try:
        rag_data = await RAGClient(settings).health()
        rag_status.ok = True
        rag_status.status_code = 200
        rag_status.detail = rag_data
    except Exception as exc:
        rag_status.detail = str(exc)

    try:
        ingest_data = await IngestClient(settings).health()
        ingest_status.ok = True
        ingest_status.status_code = 200
        ingest_status.detail = ingest_data
    except Exception as exc:
        ingest_status.detail = str(exc)

    return ServicesHealthResponse(
        backend=backend,
        rag_service=rag_status,
        ingest_service=ingest_status,
    )
