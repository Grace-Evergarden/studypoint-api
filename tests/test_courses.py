"""Course CRUD and mock-storage tests (Developer A).

Token, 401 and request-validation edge cases live in test_auth.py and
test_validation.py; this file covers CRUD behaviour, ownership on each
operation, admin access, 404s, pagination and the store's ID guarantees.
"""
import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app

BASE = "/api/v1/courses"
USER_A = {"Authorization": "Bearer user-a-token"}
USER_B = {"Authorization": "Bearer user-b-token"}
ADMIN = {"Authorization": "Bearer admin-token"}

A_COURSE, B_COURSE = "course_101", "course_201"


@pytest.fixture(autouse=True)
def fresh_store():
    """Every test starts from the same seed data, so tests can run in any order."""
    store.reset_store()
    yield
    store.reset_store()


@pytest.fixture
def client():
    return TestClient(app)


def ids(response):
    return [c["id"] for c in response.json()["data"]]


# --- Seed data ---------------------------------------------------------------

def test_seed_has_two_courses_per_student():
    owners = [c["ownerId"] for c in store.courses.values()]
    assert owners.count("user-a") >= 2
    assert owners.count("user-b") >= 2
    assert store.NONEXISTENT_COURSE_ID not in store.courses


# --- List ----------------------------------------------------------------------

def test_student_lists_only_own_courses(client):
    response = client.get(BASE, headers=USER_A)
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Courses retrieved successfully."
    assert ids(response) == ["course_101", "course_102"]
    assert body["meta"] == {"total": 2, "page": 1, "perPage": 10}


def test_user_b_lists_only_own_courses(client):
    response = client.get(BASE, headers=USER_B)
    assert ids(response) == ["course_201", "course_202"]
    assert all(c["ownerId"] == "user-b" for c in response.json()["data"])


def test_admin_lists_all_courses(client):
    response = client.get(BASE, headers=ADMIN)
    assert ids(response) == ["course_101", "course_102", "course_201", "course_202"]
    assert response.json()["meta"]["total"] == 4


def test_pagination_splits_admin_list(client):
    first = client.get(BASE, params={"page": 1, "perPage": 3}, headers=ADMIN)
    second = client.get(BASE, params={"page": 2, "perPage": 3}, headers=ADMIN)
    assert ids(first) == ["course_101", "course_102", "course_201"]
    assert ids(second) == ["course_202"]
    assert second.json()["meta"] == {"total": 4, "page": 2, "perPage": 3}


def test_page_past_the_end_is_empty_not_an_error(client):
    response = client.get(BASE, params={"page": 5}, headers=USER_A)
    assert response.status_code == 200
    assert response.json()["data"] == []
    assert response.json()["meta"]["total"] == 2


def test_ownership_filter_runs_before_pagination(client):
    # With perPage=1, a student's second page must be their own second course,
    # not whatever happens to be second in the whole store.
    response = client.get(BASE, params={"page": 2, "perPage": 1}, headers=USER_B)
    assert ids(response) == ["course_202"]
    assert response.json()["meta"]["total"] == 2


def test_list_orders_ids_numerically(client):
    store.courses["course_99"] = {"id": "course_99", "title": "Early", "description": "", "ownerId": "admin"}
    store.courses["course_1000"] = {"id": "course_1000", "title": "Late", "description": "", "ownerId": "admin"}
    response = client.get(BASE, headers=ADMIN)
    assert ids(response)[0] == "course_99"
    assert ids(response)[-1] == "course_1000"


# --- Get one -------------------------------------------------------------------

def test_owner_gets_own_course(client):
    response = client.get(f"{BASE}/{A_COURSE}", headers=USER_A)
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Course retrieved successfully.",
        "data": {
            "id": "course_101",
            "title": "Computer Graphics",
            "description": "Introduction to graphics",
            "ownerId": "user-a",
        },
    }


@pytest.mark.parametrize("course_id", [A_COURSE, B_COURSE])
def test_admin_gets_any_course(client, course_id):
    response = client.get(f"{BASE}/{course_id}", headers=ADMIN)
    assert response.status_code == 200
    assert response.json()["data"]["id"] == course_id


def test_get_unknown_course_returns_404(client):
    response = client.get(f"{BASE}/{store.NONEXISTENT_COURSE_ID}", headers=ADMIN)
    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error": {"code": "NOT_FOUND", "message": "Course not found."},
    }


# --- Cross-owner access: 403 on read, update and delete --------------------------

CROSS_OWNER = [(USER_A, B_COURSE), (USER_B, A_COURSE)]


@pytest.mark.parametrize("headers,course_id", CROSS_OWNER)
def test_student_cannot_read_other_students_course(client, headers, course_id):
    response = client.get(f"{BASE}/{course_id}", headers=headers)
    assert response.status_code == 403
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert "details" not in response.json()["error"]


@pytest.mark.parametrize("headers,course_id", CROSS_OWNER)
def test_student_cannot_update_other_students_course(client, headers, course_id):
    before = dict(store.courses[course_id])
    response = client.put(f"{BASE}/{course_id}", json={"title": "Hijacked"}, headers=headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert store.courses[course_id] == before


@pytest.mark.parametrize("headers,course_id", CROSS_OWNER)
def test_student_cannot_delete_other_students_course(client, headers, course_id):
    response = client.delete(f"{BASE}/{course_id}", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert course_id in store.courses


# --- Create --------------------------------------------------------------------

def test_student_creates_course_owned_by_themselves(client):
    response = client.post(BASE, json={"title": "Biology", "description": "Cells"}, headers=USER_A)
    assert response.status_code == 201
    assert response.json() == {
        "success": True,
        "message": "Course created successfully.",
        "data": {"id": "course_301", "title": "Biology", "description": "Cells", "ownerId": "user-a"},
    }
    assert "course_301" in ids(client.get(BASE, headers=USER_A))
    assert "course_301" not in ids(client.get(BASE, headers=USER_B))


def test_create_defaults_description_and_trims_title(client):
    response = client.post(BASE, json={"title": "  Biology  "}, headers=USER_B)
    data = response.json()["data"]
    assert data["title"] == "Biology"
    assert data["description"] == ""
    assert data["ownerId"] == "user-b"


def test_admin_creates_course_owned_by_admin(client):
    response = client.post(BASE, json={"title": "Faculty Notes"}, headers=ADMIN)
    assert response.status_code == 201
    assert response.json()["data"]["ownerId"] == "admin"


def test_created_ids_are_unique_and_not_reused_after_delete(client):
    first = client.post(BASE, json={"title": "First"}, headers=USER_A).json()["data"]["id"]
    client.delete(f"{BASE}/{first}", headers=USER_A)
    second = client.post(BASE, json={"title": "Second"}, headers=USER_A).json()["data"]["id"]
    assert first == "course_301"
    assert second == "course_302"


def test_invalid_create_does_not_store_anything(client):
    response = client.post(BASE, json={"title": "ab"}, headers=USER_A)
    assert response.status_code == 400
    assert len(store.courses) == len(store.SEED_COURSES)


# --- Update --------------------------------------------------------------------

def test_owner_replaces_course(client):
    response = client.put(
        f"{BASE}/{A_COURSE}", json={"title": "Advanced Graphics", "description": "Ray tracing"}, headers=USER_A
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Course updated successfully.",
        "data": {"id": A_COURSE, "title": "Advanced Graphics", "description": "Ray tracing", "ownerId": "user-a"},
    }
    assert client.get(f"{BASE}/{A_COURSE}", headers=USER_A).json()["data"]["title"] == "Advanced Graphics"


def test_put_without_description_resets_it(client):
    response = client.put(f"{BASE}/{A_COURSE}", json={"title": "Graphics"}, headers=USER_A)
    assert response.json()["data"]["description"] == ""


@pytest.mark.parametrize("course_id,owner", [(A_COURSE, "user-a"), (B_COURSE, "user-b")])
def test_admin_updates_any_course_without_taking_ownership(client, course_id, owner):
    response = client.put(f"{BASE}/{course_id}", json={"title": "Reviewed by admin"}, headers=ADMIN)
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Reviewed by admin"
    assert response.json()["data"]["ownerId"] == owner


def test_update_unknown_course_returns_404(client):
    response = client.put(f"{BASE}/{store.NONEXISTENT_COURSE_ID}", json={"title": "Ghost"}, headers=USER_A)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert store.NONEXISTENT_COURSE_ID not in store.courses


# --- Delete --------------------------------------------------------------------

def test_owner_deletes_course(client):
    response = client.delete(f"{BASE}/{A_COURSE}", headers=USER_A)
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Course deleted successfully.", "data": None}
    assert client.get(f"{BASE}/{A_COURSE}", headers=USER_A).status_code == 404


@pytest.mark.parametrize("course_id", [A_COURSE, B_COURSE])
def test_admin_deletes_any_course(client, course_id):
    response = client.delete(f"{BASE}/{course_id}", headers=ADMIN)
    assert response.status_code == 200
    assert course_id not in store.courses


def test_delete_unknown_course_returns_404(client):
    response = client.delete(f"{BASE}/{store.NONEXISTENT_COURSE_ID}", headers=ADMIN)
    assert response.status_code == 404


def test_deleting_twice_returns_404(client):
    assert client.delete(f"{BASE}/{A_COURSE}", headers=USER_A).status_code == 200
    assert client.delete(f"{BASE}/{A_COURSE}", headers=USER_A).status_code == 404


# --- Full lifecycle ---------------------------------------------------------------

def test_create_read_update_delete_lifecycle(client):
    created = client.post(BASE, json={"title": "Statistics"}, headers=USER_B)
    course_id = created.json()["data"]["id"]

    assert client.get(f"{BASE}/{course_id}", headers=USER_B).status_code == 200
    assert client.get(f"{BASE}/{course_id}", headers=USER_A).status_code == 403

    updated = client.put(f"{BASE}/{course_id}", json={"title": "Applied Statistics"}, headers=USER_B)
    assert updated.json()["data"]["title"] == "Applied Statistics"

    assert client.delete(f"{BASE}/{course_id}", headers=USER_B).status_code == 200
    assert client.get(f"{BASE}/{course_id}", headers=USER_B).status_code == 404

