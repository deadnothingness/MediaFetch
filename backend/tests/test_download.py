"""Tests for download task creation and retrieval."""
from fastapi.testclient import TestClient


def test_create_download_missing_fields(client: TestClient):
    """POST /download with missing fields returns 422."""
    response = client.post("/download", json={"url": "https://vkvideo/abc"})
    assert response.status_code == 422


def test_create_download_invalid_format(client: TestClient):
    """POST /download with invalid format returns 400."""
    payload = {
        "url": "https://vkvideo.be/abc",
        "format": "avi",
        "quality": "medium",
    }
    response = client.post("/download", json=payload)
    assert response.status_code == 400
    assert "Format must be" in response.text


def test_create_download_invalid_quality(client: TestClient):
    """POST /download with invalid quality returns 400."""
    payload = {
        "url": "https://vkvideo/abc",
        "format": "mp4",
        "quality": "super",
    }
    response = client.post("/download", json=payload)
    assert response.status_code == 400
    assert "Quality must be one of" in response.text


def test_create_download_valid(client: TestClient):
    """POST /download with valid payload returns task_id."""
    payload = {
        "url": "https://vkvideo.ru/video-213580023_456239058?list=ln-9sKY6zxP6QuY75nqwD",
        "format": "mp4",
        "quality": "720p",
    }
    response = client.post("/download", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    assert data["message"] == "Download started"


def test_get_tasks_empty(client: TestClient):
    """GET /tasks returns an empty list initially."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_single_task_not_found(client: TestClient):
    """GET /tasks/999 returns 404."""
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "Task not found" in response.text