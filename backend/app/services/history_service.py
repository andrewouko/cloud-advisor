"""Conversation history store backed by PostgreSQL.

Provides persistent storage for conversation history with pagination,
replacing the previous in-memory OrderedDict implementation.
"""

import logging

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.schemas.history import HistoryItem

logger = logging.getLogger(__name__)


class HistoryService:
    """PostgreSQL-backed store for conversation history.

    Attributes:
        _session: The async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        item: HistoryItem,
        model: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> None:
        """Persist a conversation to PostgreSQL.

        Args:
            item: The conversation item to store.
            model: The Claude model used.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
        """
        conversation = Conversation(
            id=item.id,
            question=item.question,
            answer=item.answer,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            timestamp=item.timestamp,
        )
        self._session.add(conversation)
        await self._session.commit()
        logger.debug("Stored conversation %s", item.id)

    async def get_all(self, limit: int = 50, offset: int = 0) -> list[HistoryItem]:
        """Return a paginated slice of conversation history (newest first).

        Args:
            limit: Maximum number of items to return.
            offset: Number of items to skip from the newest end.

        Returns:
            A list of HistoryItem objects, newest first.
        """
        stmt = (
            select(Conversation)
            .order_by(Conversation.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        return [
            HistoryItem(
                id=row.id,
                question=row.question,
                answer=row.answer,
                timestamp=row.timestamp,
            )
            for row in rows
        ]

    async def get_by_id(self, conversation_id: str) -> HistoryItem | None:
        """Retrieve a single conversation by its ID.

        Args:
            conversation_id: The UUID string of the conversation.

        Returns:
            The HistoryItem if found, otherwise None.
        """
        result = await self._session.get(Conversation, conversation_id)
        if result is None:
            return None

        return HistoryItem(
            id=result.id,
            question=result.question,
            answer=result.answer,
            timestamp=result.timestamp,
        )

    async def clear(self) -> None:
        """Remove all conversations from the store."""
        result = await self._session.execute(delete(Conversation))
        await self._session.commit()
        logger.info("History cleared — removed %d conversations", result.rowcount)

    async def count(self) -> int:
        """Return the total number of stored conversations."""
        result = await self._session.execute(select(func.count(Conversation.id)))
        return result.scalar_one()