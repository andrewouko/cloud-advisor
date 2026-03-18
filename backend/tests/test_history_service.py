"""Tests for HistoryService in-memory store."""

from datetime import datetime, timezone

from app.schemas.history import HistoryItem
from app.services.history_service import HistoryService


def _make_item(item_id: str = "abc") -> HistoryItem:
    """Helper: create a test HistoryItem."""
    return HistoryItem(
        id=item_id,
        question="Test question?",
        answer="Test answer.",
        timestamp=datetime.now(tz=timezone.utc),
    )


def test_add_and_count() -> None:
    """Adding items increments the count."""
    svc = HistoryService()
    assert svc.count() == 0
    svc.add(_make_item("1"))
    assert svc.count() == 1
    svc.add(_make_item("2"))
    assert svc.count() == 2


def test_get_all_newest_first() -> None:
    """get_all returns items newest first."""
    svc = HistoryService()
    svc.add(_make_item("first"))
    svc.add(_make_item("second"))
    items = svc.get_all()
    assert items[0].id == "second"
    assert items[1].id == "first"


def test_get_all_pagination() -> None:
    """Pagination via limit and offset works correctly."""
    svc = HistoryService()
    for i in range(5):
        svc.add(_make_item(str(i)))

    page1 = svc.get_all(limit=2, offset=0)
    page2 = svc.get_all(limit=2, offset=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id


def test_clear_removes_all_items() -> None:
    """clear() empties the store."""
    svc = HistoryService()
    svc.add(_make_item("x"))
    svc.clear()
    assert svc.count() == 0
    assert svc.get_all() == []


def test_eviction_at_capacity() -> None:
    """Oldest item is evicted when max_items is reached."""
    svc = HistoryService(max_items=3)
    svc.add(_make_item("oldest"))
    svc.add(_make_item("middle"))
    svc.add(_make_item("newest"))
    # Adding a 4th should evict "oldest"
    svc.add(_make_item("newest2"))
    all_ids = [item.id for item in svc.get_all()]
    assert "oldest" not in all_ids
    assert svc.count() == 3


def test_get_by_id() -> None:
    """get_by_id returns the correct item."""
    svc = HistoryService()
    item = _make_item("find-me")
    svc.add(item)
    found = svc.get_by_id("find-me")
    assert found is not None
    assert found.id == "find-me"


def test_get_by_id_missing_returns_none() -> None:
    """get_by_id returns None for unknown IDs."""
    svc = HistoryService()
    assert svc.get_by_id("not-there") is None