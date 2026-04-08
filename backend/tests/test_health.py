"""Tests for health check endpoint."""
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """GET /api/health should return {'status': 'ok'}."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}