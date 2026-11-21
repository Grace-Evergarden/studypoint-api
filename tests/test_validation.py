"""Tests for course request validation and standardized validation errors."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.errors import register_exception_handlers
from app.schemas import CourseCreate, CourseUpdate


@pytest.mark.parametrize("title", ["", "ab", "   "])
def test_title_must_have_at_least_three_non_whitespace_characters(title):
    with pytest.raises(ValidationError):
        CourseCreate(title=title)


def test_title_is_trimmed():
    course = CourseCreate(title="  Biology  ")
    assert course.title == "Biology"


def test_title_maximum_length_is_100():
    with pytest.raises(ValidationError):
        CourseCreate(title="x" * 101)


def test_description_maximum_length_is_500():
    with pytest.raises(ValidationError):
        CourseCreate(title="Biology", description="x" * 501)


def test_description_defaults_to_empty_string():
    assert CourseCreate(title="Biology").description == ""


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        CourseCreate(title="Biology", ownerId="user-a")


def test_update_uses_same_editable_field_rules():
    course = CourseUpdate(title="Physics")
    assert course.title == "Physics"
    assert course.description == ""


def test_request_validation_is_returned_as_http_400_envelope():
    app = FastAPI()
    register_exception_handlers(app)

    @app.post("/courses")
    def create_course(course: CourseCreate):
        return course.model_dump()

    client = TestClient(app)
    response = client.post("/courses", json={"title": "ab", "ownerId": "user-a"})

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)
    assert {item["field"] for item in body["error"]["details"]} == {"title", "ownerId"}
