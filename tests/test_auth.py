"""Tests for mock bearer authentication and course ownership checks."""
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import can_access, get_current_user


@pytest.fixture
def client():
    app = FastAPI()

    @app.get("/whoami")
    def whoami(user: dict[str, str] = Depends(get_current_user)):
        return user

    return TestClient(app)


@pytest.mark.parametrize(
    ("token", "expected_user"),
    [
        ("user-a-token", {"id": "user-a", "role": "user"}),
        ("user-b-token", {"id": "user-b", "role": "user"}),
        ("admin-token", {"id": "admin", "role": "admin"}),
    ],
)
def test_valid_tokens_return_expected_users(client, token, expected_user):
    response = client.get("/whoami", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == expected_user


def test_missing_token_returns_401(client):
    response = client.get("/whoami")
    assert response.status_code == 401


def test_invalid_token_returns_401(client):
    response = client.get("/whoami", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401


def test_non_bearer_authorization_returns_401(client):
    response = client.get("/whoami", headers={"Authorization": "Basic abc"})
    assert response.status_code == 401


def test_owner_can_access_their_course():
    user = {"id": "user-a", "role": "user"}
    course = {"id": "course_101", "ownerId": "user-a"}
    assert can_access(user, course) is True


def test_user_cannot_access_another_users_course():
    user = {"id": "user-a", "role": "user"}
    course = {"id": "course_201", "ownerId": "user-b"}
    assert can_access(user, course) is False


def test_admin_can_access_any_course():
    admin = {"id": "admin", "role": "admin"}
    course = {"id": "course_201", "ownerId": "user-b"}
    assert can_access(admin, course) is True
