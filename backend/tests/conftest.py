"""Shared pytest fixtures for CloudAdvisor backend tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.routers import query, history
from app.services.claude_service import ClaudeService, ClaudeResponse
from app.services.history_service import HistoryService
from app.services.validation_service import ResponseValidationService
from app.services.cache_service import CacheService
from app.schemas.history import HistoryItem


class MockClaudeService:
    """Stub ClaudeService that returns a predictable response without hitting the API."""

    async def generate_response(self, question: str) -> ClaudeResponse:
        return ClaudeResponse(
            content="## Mock Response\n\nThis is a test answer about cloud migration strategies.",
            model="claude-haiku-4-5-20251001",
            input_tokens=10,
            output_tokens=20,
        )


class MockHistoryService:
    """In-memory history service stub for testing (avoids PostgreSQL dependency)."""

    def __init__(self):
        self._store: dict[str, HistoryItem] = {}

    async def add(self, item: HistoryItem, model: str = "", input_tokens: int = 0, output_tokens: int = 0) -> None:
        self._store[item.id] = item

    async def get_all(self, limit: int = 50, offset: int = 0) -> list[HistoryItem]:
        all_items = list(reversed(self._store.values()))
        return all_items[offset : offset + limit]

    async def get_by_id(self, conversation_id: str) -> HistoryItem | None:
        return self._store.get(conversation_id)

    async def clear(self) -> None:
        self._store.clear()

    async def count(self) -> int:
        return len(self._store)


class MockCacheService:
    """Stub CacheService that provides no-op caching for tests."""

    @property
    def is_connected(self) -> bool:
        return False

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def get_cached_response(self, question: str):
        return None

    async def cache_response(self, **kwargs) -> None:
        pass

    async def check_rate_limit(self, client_ip: str) -> tuple[bool, int]:
        return True, 20


@pytest.fixture
def mock_history_service() -> MockHistoryService:
    """Return a fresh mock HistoryService instance for each test."""
    return MockHistoryService()


@pytest.fixture
def client(mock_history_service: MockHistoryService) -> TestClient:
    """Return a TestClient with mocked services and fresh HistoryService."""
    app = create_app()
    mock_claude = MockClaudeService()
    mock_cache = MockCacheService()
    validation_service = ResponseValidationService()

    app.dependency_overrides[query.get_claude_service] = lambda: mock_claude
    app.dependency_overrides[query.get_validation_service] = lambda: validation_service
    app.dependency_overrides[query.get_cache_service] = lambda: mock_cache
    app.dependency_overrides[query.get_history_service] = lambda: mock_history_service
    app.dependency_overrides[history.get_history_service] = lambda: mock_history_service

    return TestClient(app)