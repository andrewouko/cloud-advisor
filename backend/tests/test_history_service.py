"""Tests for HistoryService (using mock in-memory implementation)."""

import pytest
from datetime import datetime, timezone

from app.schemas.history import HistoryItem
from tests.conftest import MockHistoryService


def _make_item(item_id: str = "abc") -> HistoryItem:
    """Helper: create a test HistoryItem."""
    return HistoryItem(
        id=item_id,
        question="Test question?",
        answer="Test answer.",
        timestamp=datetime.now(tz=timezone.utc),
    )


@pytest.fixture
def history_svc() -> MockHistoryService:
    """Fresh mock history service for each test."""
    return MockHistoryService()


@pytest.mark.asyncio
async def test_add_and_count(history_svc: MockHistoryService) -> None:
    """Adding items increments the count."""
    assert await history_svc.count() == 0
    await history_svc.add(_make_item("1"))
    assert await history_svc.count() == 1
    await history_svc.add(_make_item("2"))
    assert await history_svc.count() == 2


@pytest.mark.asyncio
async def test_get_all_newest_first(history_svc: MockHistoryService) -> None:
    """get_all returns items newest first."""
    await history_svc.add(_make_item("first"))
    await history_svc.add(_make_item("second"))
    items = await history_svc.get_all()
    assert items[0].id == "second"
    assert items[1].id == "first"


@pytest.mark.asyncio
async def test_get_all_pagination(history_svc: MockHistoryService) -> None:
    """Pagination via limit and offset works correctly."""
    for i in range(5):
        await history_svc.add(_make_item(str(i)))

    page1 = await history_svc.get_all(limit=2, offset=0)
    page2 = await history_svc.get_all(limit=2, offset=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id


@pytest.mark.asyncio
async def test_clear_removes_all_items(history_svc: MockHistoryService) -> None:
    """clear() empties the store."""
    await history_svc.add(_make_item("x"))
    await history_svc.clear()
    assert await history_svc.count() == 0
    assert await history_svc.get_all() == []


@pytest.mark.asyncio
async def test_get_by_id(history_svc: MockHistoryService) -> None:
    """get_by_id returns the correct item."""
    item = _make_item("find-me")
    await history_svc.add(item)
    found = await history_svc.get_by_id("find-me")
    assert found is not None
    assert found.id == "find-me"


@pytest.mark.asyncio
async def test_get_by_id_missing_returns_none(history_svc: MockHistoryService) -> None:
    """get_by_id returns None for unknown IDs."""
    assert await history_svc.get_by_id("not-there") is None