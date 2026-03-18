"""Query router — POST /api/query.

Accepts a user question, delegates to ClaudeService for the AI response,
stores the result in HistoryService, and returns a structured response.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.query import QueryRequest, QueryResponse
from app.services.claude_service import ClaudeService
from app.services.history_service import HistoryService
from app.schemas.history import HistoryItem

logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])


def get_claude_service() -> ClaudeService:
    """Dependency: return the shared ClaudeService instance."""
    raise NotImplementedError("ClaudeService dependency not wired")  # pragma: no cover


def get_history_service() -> HistoryService:
    """Dependency: return the shared HistoryService instance."""
    raise NotImplementedError("HistoryService dependency not wired")  # pragma: no cover


@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=200,
    summary="Ask a cloud/IT question",
    description=(
        "Submit a question about cloud technology or IT solutions. "
        "Returns a structured, markdown-formatted response from Claude."
    ),
)
async def ask_question(
    payload: QueryRequest,
    claude_service: ClaudeService = Depends(get_claude_service),
    history_service: HistoryService = Depends(get_history_service),
) -> QueryResponse:
    """Handle an incoming user question and return an AI response.

    Args:
        payload: Validated request containing the user's question.
        claude_service: Injected AI response generator.
        history_service: Injected conversation store.

    Returns:
        QueryResponse containing the AI answer and request metadata.

    Raises:
        HTTPException: 400 if the question contains only whitespace.
    """
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty or whitespace only.")

    logger.info("Received question: %.80s...", question)

    claude_response = await claude_service.generate_response(question)

    conversation_id = str(uuid.uuid4())
    timestamp = datetime.now(tz=timezone.utc)

    history_item = HistoryItem(
        id=conversation_id,
        question=question,
        answer=claude_response.content,
        timestamp=timestamp,
    )
    history_service.add(history_item)

    return QueryResponse(
        id=conversation_id,
        question=question,
        answer=claude_response.content,
        timestamp=timestamp,
        model=claude_response.model,
        tokens_used=claude_response.total_tokens,
    )