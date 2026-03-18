"""Health check router.

Provides a liveness endpoint used by deployment platforms
(Railway, Docker healthcheck) to verify the service is running,
including database and Redis connectivity status.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.database import engine

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str
    version: str
    timestamp: datetime
    database: str
    cache: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the current health status of the API, including database and cache connectivity.",
)
async def health_check() -> HealthResponse:
    """Return health status including database and Redis connectivity.

    Returns:
        HealthResponse with status, version, timestamp, and service health.
    """
    from app.config import get_settings

    settings = get_settings()

    # Check database
    db_status = "unavailable"
    if engine:
        try:
            async with engine.connect() as conn:
                await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            db_status = "connected"
        except Exception:
            db_status = "error"

    # Check Redis (import here to avoid circular imports at module level)
    cache_status = "unavailable"
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.redis_url, decode_responses=True)
        await r.ping()
        await r.aclose()
        cache_status = "connected"
    except Exception:
        cache_status = "unavailable"

    overall = "healthy" if db_status == "connected" else "degraded"

    return HealthResponse(
        status=overall,
        version=settings.app_version,
        timestamp=datetime.now(tz=timezone.utc),
        database=db_status,
        cache=cache_status,
    )