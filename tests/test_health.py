"""Unit tests for Render health check endpoint."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_200_ok():
    """Validates health check endpoint used by Render auto-deploy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "app" in data
