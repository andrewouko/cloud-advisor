"""In-memory conversation history store.

Provides O(1) lookup with insertion-order preservation via OrderedDict.
In a production system this would be backed by PostgreSQL or Redis.
"""

import logging
from collections import OrderedDict

from app.schemas.history import HistoryItem

logger = logging.getLogger(__name__)


class HistoryService:
    """Thread-safe in-memory store for conversation history.

    Items are stored in insertion order and automatically evicted when
    the maximum capacity is reached (oldest item removed first).

    Attributes:
        _store: Ordered mapping of conversation ID to HistoryItem.
        _max_items: Maximum number of conversations to retain in memory.
    """

    def __init__(self, max_items: int = 100) -> None:
        """Initialise the history store.

        Args:
            max_items: Maximum number of conversations to keep.
                       Oldest entries are evicted when this limit is reached.
        """
        self._store: OrderedDict[str, HistoryItem] = OrderedDict()
        self._max_items = max_items

    def add(self, item: HistoryItem) -> None:
        """Add a conversation to the history store.

        If the store is at capacity, the oldest entry is removed first.

        Args:
            item: The conversation item to store.
        """
        if len(self._store) >= self._max_items:
            evicted_id, _ = self._store.popitem(last=False)
            logger.debug("History capacity reached — evicted conversation %s", evicted_id)

        self._store[item.id] = item
        logger.debug("Stored conversation %s (total: %d)", item.id, len(self._store))

    def get_all(self, limit: int = 50, offset: int = 0) -> list[HistoryItem]:
        """Return a paginated slice of conversation history (newest first).

        Args:
            limit: Maximum number of items to return.
            offset: Number of items to skip from the newest end.

        Returns:
            A list of HistoryItem objects, newest first.
        """
        all_items = list(reversed(self._store.values()))
        return all_items[offset : offset + limit]

    def get_by_id(self, conversation_id: str) -> HistoryItem | None:
        """Retrieve a single conversation by its ID.

        Args:
            conversation_id: The UUID string of the conversation.

        Returns:
            The HistoryItem if found, otherwise None.
        """
        return self._store.get(conversation_id)

    def clear(self) -> None:
        """Remove all conversations from the store."""
        count = len(self._store)
        self._store.clear()
        logger.info("History cleared — removed %d conversations", count)

    def count(self) -> int:
        """Return the total number of stored conversations."""
        return len(self._store)