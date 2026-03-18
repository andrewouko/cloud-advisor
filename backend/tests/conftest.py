"""Shared pytest fixtures for CloudAdvisor backend tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.routers import query, history
from app.services.claude_service import ClaudeService, ClaudeResponse
from app.services.history_service import HistoryService


class MockClaudeService:
    """Stub ClaudeService that returns a predictable response without hitting the API."""

    async def generate_response(self, question: str) -> ClaudeResponse:
        """Return a deterministic fake response for testing.

        Args:
            question: The user question (unused in mock).

        Returns:
            A ClaudeResponse with fixed content and metadata.
        """
        return ClaudeResponse(
            content="## Mock Response\n\nThis is a test answer.",
            model="claude-haiku-4-5-20251001",
            input_tokens=10,
            output_tokens=20,
        )


@pytest.fixture
def history_service() -> HistoryService:
    """Return a fresh HistoryService instance for each test."""
    return HistoryService()


@pytest.fixture
def client(history_service: HistoryService) -> TestClient:
    """Return a TestClient with mocked ClaudeService and fresh HistoryService.

    Args:
        history_service: Fresh history store injected into the app.

    Returns:
        A FastAPI TestClient ready for requests.
    """
    app = create_app()
    mock_claude = MockClaudeService()

    app.dependency_overrides[query.get_claude_service] = lambda: mock_claude
    app.dependency_overrides[query.get_history_service] = lambda: history_service
    app.dependency_overrides[history.get_history_service] = lambda: history_service

    return TestClient(app)