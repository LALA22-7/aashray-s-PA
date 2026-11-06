"""Tests for the health-check and root endpoints."""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    """GET /api/health and /api/v1/health return 200 with status 'healthy'."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

    # Test /api/v1 alias
    v1_resp = client.get("/api/v1/health")
    assert v1_resp.status_code == 200
    assert v1_resp.json()["status"] == "healthy"

    # Test direct /health alias
    direct_resp = client.get("/health")
    assert direct_resp.status_code == 200
    assert direct_resp.json()["status"] == "healthy"


def test_health_returns_app_info(client: TestClient) -> None:
    """GET /api/health response includes version and app_name."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "app_name" in data


def test_health_db_endpoint(client: TestClient) -> None:
    """GET /api/health/db returns 200 with database 'connected'."""
    response = client.get("/api/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"


def test_root_endpoint(client: TestClient) -> None:
    """GET / returns 200."""
    response = client.get("/")
    assert response.status_code == 200
