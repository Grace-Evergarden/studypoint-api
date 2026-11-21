from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_greeting_returns_html():
    response = client.get("/api/v1/greeting")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "StudyPoint" in response.text


def test_greeting_contains_required_information():
    response = client.get("/api/v1/greeting")

    assert "Project Team" in response.text
    assert "Available API Endpoints" in response.text
    assert "GET /api/v1/courses" in response.text
    assert "POST /api/v1/courses" in response.text
    assert "API running" in response.text
