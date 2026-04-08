"""Tests that static files are served correctly."""
from fastapi.testclient import TestClient


def test_index_html(client: TestClient):
    """GET / should return HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "MediaFetch" in response.text


def test_css(client: TestClient):
    """GET /style.css should return CSS."""
    response = client.get("/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_js(client: TestClient):
    """GET /app.js should return JavaScript."""
    response = client.get("/app.js")
    assert response.status_code == 200
    assert "application/javascript" in response.headers["content-type"]