"""History router — GET and DELETE /api/history."""

import logging

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.schemas.history import HistoryResponse
from app.services.history_service import HistoryService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["history"])


def get_history_service() -> HistoryService:
    """Dependency: return the shared HistoryService instance.

    The actual singleton is injected at application startup via
    dependency_overrides or the app state — this stub is replaced
    in main.py and in tests.
    """
    raise NotImplementedError("HistoryService dependency not wired")  # pragma: no cover


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Get conversation history",
    description="Returns paginated conversation history, newest first.",
)
async def get_history(
    limit: int = Query(default=50, ge=1, le=100, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    history_service: HistoryService = Depends(get_history_service),
) -> HistoryResponse:
    """Retrieve paginated conversation history.

    Args:
        limit: Maximum number of conversations to return (1–100).
        offset: Number of conversations to skip from the newest end.
        history_service: Injected history store.

    Returns:
        HistoryResponse with a list of conversations and pagination metadata.
    """
    conversations = history_service.get_all(limit=limit, offset=offset)
    total = history_service.count()

    logger.debug("Returning %d/%d history items", len(conversations), total)

    return HistoryResponse(
        conversations=conversations,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete(
    "/history",
    status_code=204,
    summary="Clear conversation history",
    description="Deletes all stored conversations from the in-memory store.",
)
async def clear_history(
    history_service: HistoryService = Depends(get_history_service),
) -> Response:
    """Clear all conversation history.

    Args:
        history_service: Injected history store.

    Returns:
        204 No Content on success.
    """
    history_service.clear()
    logger.info("Conversation history cleared via API")
    return Response(status_code=204)