from fastapi import FastAPI
from app.api.routes_health import router as health_router
from app.api.routes_ingest import router as ingest_router

app = FastAPI(title="Sovra AI Ingest Service", version="0.1.0")
app.include_router(health_router)
app.include_router(ingest_router)