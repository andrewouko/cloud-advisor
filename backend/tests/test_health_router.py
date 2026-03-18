"""Tests for GET /api/health."""

from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient) -> None:
    """Health endpoint should return 200."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_check_response_schema(client: TestClient) -> None:
    """Health response should include required fields."""
    response = client.get("/api/health")
    data = response.json()

    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "timestamp" in data
    assert "database" in data
    assert "cache" in data


def test_health_check_version(client: TestClient) -> None:
    """Version field should be a non-empty string."""
    response = client.get("/api/health")
    version = response.json()["version"]
    assert isinstance(version, str)
    assert len(version) > 0