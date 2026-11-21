"""In-memory mock storage for StudyPoint courses.

All data lives in process memory and is reset to the seed below whenever the
server restarts (or when ``reset_store()`` is called, e.g. by tests).

Shared contract (team contract, section 4):
    courses: dict[str, dict]   -- mutable store, keyed by course ID
    new_course_id() -> str     -- next unique ID, never reused after deletes
"""
from copy import deepcopy
from itertools import count

# Documented nonexistent ID used to demonstrate 404 Not Found.
NONEXISTENT_COURSE_ID = "course_999"

# Deterministic seed data: two courses per student. The admin can see all four.
SEED_COURSES: tuple[dict, ...] = (
    {
        "id": "course_101",
        "title": "Computer Graphics",
        "description": "Introduction to graphics",
        "ownerId": "user-a",
    },
    {
        "id": "course_102",
        "title": "Data Structures",
        "description": "Lists, trees, graphs and hash tables",
        "ownerId": "user-a",
    },
    {
        "id": "course_201",
        "title": "Linear Algebra",
        "description": "Vectors, matrices and linear transformations",
        "ownerId": "user-b",
    },
    {
        "id": "course_202",
        "title": "Operating Systems",
        "description": "",
        "ownerId": "user-b",
    },
)

# New courses start at course_301, above every seed ID, so they never collide.
FIRST_NEW_ID = 301

courses: dict[str, dict] = {}
_id_counter = count(FIRST_NEW_ID)


def new_course_id() -> str:
    """Return the next unused course ID.

    The counter only ever moves forward, so an ID freed by a delete is never
    handed out again during the life of the process.
    """
    return f"course_{next(_id_counter)}"


def course_sort_key(course_id: str) -> int:
    """Sort key for stable, numeric ID ordering (course_99 < course_101)."""
    return int(course_id.rsplit("_", 1)[1])


def reset_store() -> None:
    """Restore the seed data and the ID counter.

    Mutates ``courses`` in place so every module that imported it keeps
    seeing the same object.
    """
    global _id_counter
    courses.clear()
    for course in SEED_COURSES:
        courses[course["id"]] = deepcopy(course)
    _id_counter = count(FIRST_NEW_ID)


reset_store()
