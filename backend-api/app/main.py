from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.api.routes_ingest import router as ingest_router
from app.core.config import get_settings
from app.db.sqlite import SQLiteStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    SQLiteStore(settings.database_url).init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        health_router,
        prefix=settings.api_v1_prefix,
    )

    app.include_router(
        chat_router,
        prefix=settings.api_v1_prefix,
    )

    app.include_router(
        ingest_router,
        prefix=settings.api_v1_prefix,
    )

    return app


app = create_app()
