"""Query router — POST /api/query.

Accepts a user question, checks cache, delegates to ClaudeService for the
AI response, validates the response, stores the result in HistoryService,
and returns a structured response.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas.query import QueryRequest, QueryResponse
from app.services.cache_service import CacheService
from app.services.claude_service import ClaudeService
from app.services.history_service import HistoryService
from app.schemas.history import HistoryItem
from app.services.validation_service import (
    MAX_VALIDATION_RETRIES,
    ResponseValidationService,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])


def get_claude_service() -> ClaudeService:
    """Dependency: return the shared ClaudeService instance."""
    raise NotImplementedError("ClaudeService dependency not wired")  # pragma: no cover


def get_history_service() -> HistoryService:
    """Dependency: return the shared HistoryService instance."""
    raise NotImplementedError("HistoryService dependency not wired")  # pragma: no cover


def get_validation_service() -> ResponseValidationService:
    """Dependency: return the shared ResponseValidationService instance."""
    raise NotImplementedError("ValidationService dependency not wired")  # pragma: no cover


def get_cache_service() -> CacheService:
    """Dependency: return the shared CacheService instance."""
    raise NotImplementedError("CacheService dependency not wired")  # pragma: no cover


@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=200,
    summary="Ask a cloud/IT question",
    description=(
        "Submit a question about cloud technology or IT solutions. "
        "Returns a structured, markdown-formatted response from Claude. "
        "Responses are validated for quality and cached for performance."
    ),
)
async def ask_question(
    payload: QueryRequest,
    request: Request,
    claude_service: ClaudeService = Depends(get_claude_service),
    history_service: HistoryService = Depends(get_history_service),
    validation_service: ResponseValidationService = Depends(get_validation_service),
    cache_service: CacheService = Depends(get_cache_service),
) -> QueryResponse:
    """Handle an incoming user question and return an AI response.

    Flow:
    1. Rate limit check (via Redis)
    2. Cache lookup (returns cached response if available)
    3. Claude API call with retry on validation failure
    4. Response validation (structure, relevance, safety)
    5. Cache the response
    6. Persist to PostgreSQL history
    """
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty or whitespace only.")

    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    allowed, remaining = await cache_service.check_rate_limit(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again shortly.",
        )

    logger.info("Received question: %.80s...", question)

    # Check cache first
    cached = await cache_service.get_cached_response(question)
    if cached:
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now(tz=timezone.utc)

        history_item = HistoryItem(
            id=conversation_id,
            question=question,
            answer=cached.content,
            timestamp=timestamp,
        )
        await history_service.add(
            history_item,
            model=cached.model,
            input_tokens=cached.input_tokens,
            output_tokens=cached.output_tokens,
        )

        return QueryResponse(
            id=conversation_id,
            question=question,
            answer=cached.content,
            timestamp=timestamp,
            model=cached.model,
            tokens_used=cached.input_tokens + cached.output_tokens,
            cached=True,
        )

    # Generate response with validation retry loop
    claude_response = None
    last_validation = None

    for attempt in range(1 + MAX_VALIDATION_RETRIES):
        claude_response = await claude_service.generate_response(question)
        last_validation = validation_service.validate(claude_response.content, question)

        if last_validation.is_valid:
            break

        if attempt < MAX_VALIDATION_RETRIES:
            logger.warning(
                "Validation failed (attempt %d/%d): %s — retrying",
                attempt + 1,
                1 + MAX_VALIDATION_RETRIES,
                last_validation.summary,
            )

    # Log if validation still failed after retries but return the response anyway
    # (better to show a potentially imperfect response than nothing)
    if last_validation and not last_validation.is_valid:
        logger.warning(
            "Response served despite validation issues: %s",
            last_validation.summary,
        )

    conversation_id = str(uuid.uuid4())
    timestamp = datetime.now(tz=timezone.utc)

    # Cache the response
    await cache_service.cache_response(
        question=question,
        content=claude_response.content,
        model=claude_response.model,
        input_tokens=claude_response.input_tokens,
        output_tokens=claude_response.output_tokens,
    )

    history_item = HistoryItem(
        id=conversation_id,
        question=question,
        answer=claude_response.content,
        timestamp=timestamp,
    )
    await history_service.add(
        history_item,
        model=claude_response.model,
        input_tokens=claude_response.input_tokens,
        output_tokens=claude_response.output_tokens,
    )

    return QueryResponse(
        id=conversation_id,
        question=question,
        answer=claude_response.content,
        timestamp=timestamp,
        model=claude_response.model,
        tokens_used=claude_response.total_tokens,
        cached=False,
    )