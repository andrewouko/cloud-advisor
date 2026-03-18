"""Tests for POST /api/query."""

from fastapi.testclient import TestClient


def test_query_success(client: TestClient) -> None:
    """Valid question should return 200 with expected response schema."""
    response = client.post("/api/query", json={"question": "What is Google Workspace?"})
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["question"] == "What is Google Workspace?"
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "timestamp" in data
    assert "model" in data
    assert "cached" in data


def test_query_empty_question_returns_400(client: TestClient) -> None:
    """Empty string question should return 400."""
    response = client.post("/api/query", json={"question": ""})
    assert response.status_code == 422  # Pydantic min_length=1 rejects this


def test_query_whitespace_only_returns_400(client: TestClient) -> None:
    """Whitespace-only question should return 400."""
    response = client.post("/api/query", json={"question": "   "})
    assert response.status_code == 400


def test_query_too_long_returns_422(client: TestClient) -> None:
    """Question exceeding max_length should return 422."""
    long_question = "a" * 2001
    response = client.post("/api/query", json={"question": long_question})
    assert response.status_code == 422


def test_query_response_has_tokens_used(client: TestClient) -> None:
    """Response should include a numeric tokens_used field."""
    response = client.post("/api/query", json={"question": "How do I use GCP?"})
    data = response.json()
    assert data["tokens_used"] == 30  # MockClaudeService returns 10+20


def test_query_populates_history(client: TestClient) -> None:
    """After a query, history endpoint should contain the conversation."""
    client.post("/api/query", json={"question": "What is cloud computing?"})
    history_response = client.get("/api/history")
    assert history_response.status_code == 200
    assert history_response.json()["total"] == 1


def test_query_missing_question_field_returns_422(client: TestClient) -> None:
    """Missing required question field should return 422."""
    response = client.post("/api/query", json={})
    assert response.status_code == 422


def test_query_cached_field_is_false_for_fresh(client: TestClient) -> None:
    """Fresh responses should have cached=False."""
    response = client.post("/api/query", json={"question": "What is GCP?"})
    data = response.json()
    assert data["cached"] is False