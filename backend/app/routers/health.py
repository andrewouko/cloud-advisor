"""Health check router.

Provides a simple liveness endpoint used by deployment platforms
(Railway, Docker healthcheck) to verify the service is running.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str
    version: str
    timestamp: datetime


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the current health status of the API.",
)
async def health_check() -> HealthResponse:
    """Return a healthy status response.

    Returns:
        HealthResponse with status, version, and current UTC timestamp.
    """
    from app.config import get_settings

    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(tz=timezone.utc),
    )