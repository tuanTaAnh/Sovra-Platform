import httpx
from fastapi import HTTPException

from app.core.config import Settings


class IngestClient:
    def __init__(self, settings: Settings):
        self.base_url = settings.ingest_service_url.rstrip("/")
        self.timeout = settings.http_timeout_seconds

    async def health(self) -> dict:
        return await self._request("GET", "/health")

    async def run(self, reindex: bool) -> dict:
        return await self._request(
            "POST",
            "/ingest/run",
            json={"reindex": reindex},
        )

    async def stats(self) -> dict:
        return await self._request("GET", "/ingest/stats")

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, **kwargs)

        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=504,
                detail=f"Ingest service timeout: {exc}",
            ) from exc

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Cannot connect to ingest service: {exc}",
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Ingest service returned an error.",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        return response.json()
