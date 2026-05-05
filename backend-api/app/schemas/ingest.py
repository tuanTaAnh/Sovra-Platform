from pydantic import BaseModel
from typing import Any


class IngestRunRequest(BaseModel):
    reindex: bool = False


class ProxyResponse(BaseModel):
    data: dict[str, Any]
