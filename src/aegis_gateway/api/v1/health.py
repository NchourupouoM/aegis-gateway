from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1", tags=["Health & Status"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        app_name="Aegis-LLM-Gateway",
        environment="development",
        version="0.1.0",
    )