"""Course CRUD endpoints (team contract, sections 4-6).

Access rules:
    * Every route needs a valid bearer token (401 otherwise, via get_current_user).
    * Students see and manage only their own courses; the admin manages all.
    * Another owner's course -> 403 FORBIDDEN; unknown ID -> 404 NOT_FOUND.
      The 404 check runs first, so a 403 only ever refers to a course that exists.

Request bodies and query parameters are validated by FastAPI/Pydantic; the
shared exception handlers turn those failures into 400 VALIDATION_ERROR.
"""
from copy import deepcopy
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app import store
from app.auth import can_access, get_current_user
from app.errors import error_response, success_response
from app.schemas import CourseCreate, CourseUpdate

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])

CurrentUser = dict[str, str]

NOT_FOUND_MESSAGE = "Course not found."
FORBIDDEN_MESSAGE = "You do not have permission to access this course."

# Documented in the OpenAPI schema at /docs; the bodies follow the shared envelope.
_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"description": "VALIDATION_ERROR: invalid or missing fields or query parameters"},
    401: {"description": "UNAUTHORIZED: missing or invalid bearer token"},
}
_ITEM_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    **_ERROR_RESPONSES,
    403: {"description": "FORBIDDEN: the course belongs to another user"},
    404: {"description": "NOT_FOUND: no course with this ID"},
}


def _find_accessible_course(course_id: str, user: CurrentUser) -> dict | JSONResponse:
    """Return the stored course, or the 404/403 error response to send instead."""
    course = store.courses.get(course_id)
    if course is None:
        return error_response(404, "NOT_FOUND", NOT_FOUND_MESSAGE)
    if not can_access(user, course):
        return error_response(403, "FORBIDDEN", FORBIDDEN_MESSAGE)
    return course


@router.get("", summary="List courses", responses=_ERROR_RESPONSES)
def list_courses(
    page: int = Query(1, ge=1, description="Page number, starting at 1."),
    perPage: int = Query(10, ge=1, le=100, description="Courses per page (1-100)."),
    user: CurrentUser = Depends(get_current_user),
) -> JSONResponse:
    """Students get their own courses; the admin gets every course.

    Ownership filtering happens before pagination, so `meta.total` counts only
    the courses this user may see. Results are ordered by numeric course ID.
    """
    visible = [c for c in store.courses.values() if can_access(user, c)]
    visible.sort(key=lambda c: store.course_sort_key(c["id"]))

    start = (page - 1) * perPage
    page_items = deepcopy(visible[start : start + perPage])

    return success_response(
        "Courses retrieved successfully.",
        page_items,
        meta={"total": len(visible), "page": page, "perPage": perPage},
    )


@router.get("/{course_id}", summary="Get one course", responses=_ITEM_ERROR_RESPONSES)
def get_course(course_id: str, user: CurrentUser = Depends(get_current_user)) -> JSONResponse:
    found = _find_accessible_course(course_id, user)
    if isinstance(found, JSONResponse):
        return found
    return success_response("Course retrieved successfully.", deepcopy(found))


@router.post("", status_code=201, summary="Create a course", responses=_ERROR_RESPONSES)
def create_course(body: CourseCreate, user: CurrentUser = Depends(get_current_user)) -> JSONResponse:
    """The new course is owned by the caller; `id` and `ownerId` are set by the server."""
    course = {
        "id": store.new_course_id(),
        "title": body.title,
        "description": body.description,
        "ownerId": user["id"],
    }
    store.courses[course["id"]] = course
    return success_response("Course created successfully.", deepcopy(course), status_code=201)


@router.put("/{course_id}", summary="Replace a course", responses=_ITEM_ERROR_RESPONSES)
def update_course(
    course_id: str, body: CourseUpdate, user: CurrentUser = Depends(get_current_user)
) -> JSONResponse:
    """Replaces the editable fields. An omitted `description` resets it to "".

    `id` and `ownerId` never change, including when the admin edits a student's course.
    """
    found = _find_accessible_course(course_id, user)
    if isinstance(found, JSONResponse):
        return found
    found["title"] = body.title
    found["description"] = body.description
    return success_response("Course updated successfully.", deepcopy(found))


@router.delete("/{course_id}", summary="Delete a course", responses=_ITEM_ERROR_RESPONSES)
def delete_course(course_id: str, user: CurrentUser = Depends(get_current_user)) -> JSONResponse:
    found = _find_accessible_course(course_id, user)
    if isinstance(found, JSONResponse):
        return found
    del store.courses[course_id]
    return success_response("Course deleted successfully.", None)
