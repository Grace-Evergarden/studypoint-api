<!-- Courses section contributed by Developer A. Developer C owns this file and merges sections. -->

## Courses

`courses` is the main resource. A course looks like this:

```json
{
  "id": "course_101",
  "title": "Computer Graphics",
  "description": "Introduction to graphics",
  "ownerId": "user-a"
}
```

| Field | Type | Set by | Rules |
|---|---|---|---|
| `id` | string | server | `course_<number>`. New IDs start at `course_301` and are never reused, even after a delete. |
| `title` | string | client | Required. Surrounding spaces are trimmed, then it must be 3–100 characters. |
| `description` | string | client | Optional, at most 500 characters, defaults to `""`. |
| `ownerId` | string | server | The ID of the user who created the course. Clients cannot send or change it. |

### Common rules for all course endpoints

**Headers**

| Header | Required | Value |
|---|---|---|
| `Authorization` | yes | `Bearer user-a-token`, `Bearer user-b-token` or `Bearer admin-token` |
| `Content-Type` | for `POST` and `PUT` | `application/json` |

**Who can do what**

| Caller | List | Create | Read / update / delete |
|---|---|---|---|
| `user-a`, `user-b` | Only their own courses | Course owned by themselves | Only their own courses |
| `admin` | All courses | Course owned by `admin` | Any course |

**Why 403 rather than 404 for someone else's course.** The assignment lets us choose. We return `403 FORBIDDEN` because it tells the client exactly what happened: the course exists but belongs to someone else. That makes ownership bugs easy to spot in the demo and in tests. The trade-off is that a student can find out whether a course ID exists. That's acceptable here because course IDs are sequential and course titles aren't sensitive. A production system holding private data might return 404 instead. The existence check runs first, so an unknown ID always gives `404`, whoever asks.

**Errors any course endpoint can return**

| Status | `error.code` | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid body or query parameter. The response includes `error.details`. |
| 401 | `UNAUTHORIZED` | `Authorization` header missing, malformed or with an unknown token. |
| 405 | `METHOD_NOT_ALLOWED` | Unsupported method, e.g. `PATCH /api/v1/courses/course_101`. |

Authentication is checked before the body. A request with no token and an invalid body gets `401`, not `400`.

**Seed data** (reset every time the server restarts):

| ID | Title | Owner |
|---|---|---|
| `course_101` | Computer Graphics | `user-a` |
| `course_102` | Data Structures | `user-a` |
| `course_201` | Linear Algebra | `user-b` |
| `course_202` | Operating Systems | `user-b` |
| `course_999` | *does not exist* (use it to demo 404) | — |

---

### `GET /api/v1/courses` — List courses

Returns the courses the caller may see, ordered by numeric ID. Ownership filtering happens **before** pagination, so `meta.total` counts only the caller's visible courses.

**Query parameters**

| Name | Type | Default | Rules |
|---|---|---|---|
| `page` | integer | `1` | `>= 1` |
| `perPage` | integer | `10` | `1`–`100` |

A page past the end returns `200` with `data: []`.

**Success — `200 OK`**

```http
GET /api/v1/courses?page=1&perPage=10
Authorization: Bearer user-a-token
```

```json
{
  "success": true,
  "message": "Courses retrieved successfully.",
  "data": [
    { "id": "course_101", "title": "Computer Graphics", "description": "Introduction to graphics", "ownerId": "user-a" },
    { "id": "course_102", "title": "Data Structures", "description": "Lists, trees, graphs and hash tables", "ownerId": "user-a" }
  ],
  "meta": { "total": 2, "page": 1, "perPage": 10 }
}
```

**Errors:** `400` (e.g. `page=0`, `perPage=101`, `page=abc`), `401`.

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid or missing fields.",
    "details": [{ "field": "page", "message": "Input should be greater than or equal to 1" }]
  }
}
```

---

### `GET /api/v1/courses/{id}` — Get one course

**Path parameters:** `id` — course ID, e.g. `course_101`.

**Success — `200 OK`**

```http
GET /api/v1/courses/course_101
Authorization: Bearer user-a-token
```

```json
{
  "success": true,
  "message": "Course retrieved successfully.",
  "data": { "id": "course_101", "title": "Computer Graphics", "description": "Introduction to graphics", "ownerId": "user-a" }
}
```

**Errors:** `401`, `403`, `404`.

```http
GET /api/v1/courses/course_201
Authorization: Bearer user-a-token
```

```json
{
  "success": false,
  "error": { "code": "FORBIDDEN", "message": "You do not have permission to access this course." }
}
```

```http
GET /api/v1/courses/course_999
Authorization: Bearer admin-token
```

```json
{
  "success": false,
  "error": { "code": "NOT_FOUND", "message": "Course not found." }
}
```

---

### `POST /api/v1/courses` — Create a course

**Body:** `title` (required), `description` (optional). Any other field, including `id` or `ownerId`, is rejected with `400`. The new course is owned by the caller.

**Success — `201 Created`**

```http
POST /api/v1/courses
Authorization: Bearer user-a-token
Content-Type: application/json

{ "title": "Biology", "description": "Cells and genetics" }
```

```json
{
  "success": true,
  "message": "Course created successfully.",
  "data": { "id": "course_301", "title": "Biology", "description": "Cells and genetics", "ownerId": "user-a" }
}
```

**Errors:** `400` (missing title, wrong type, title too short/long, description too long, unknown field), `401`.

```http
POST /api/v1/courses
Authorization: Bearer user-a-token
Content-Type: application/json

{ "title": "AI" }
```

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid or missing fields.",
    "details": [{ "field": "title", "message": "String should have at least 3 characters." }]
  }
}
```

---

### `PUT /api/v1/courses/{id}` — Replace a course

Replaces the editable fields. `title` is required. If `description` is left out, it is reset to `""`. `id` and `ownerId` never change, even when the admin edits a student's course.

**Path parameters:** `id` — course ID.
**Body:** same rules as `POST`.

**Success — `200 OK`**

```http
PUT /api/v1/courses/course_201
Authorization: Bearer admin-token
Content-Type: application/json

{ "title": "Linear Algebra II", "description": "Eigenvalues and SVD" }
```

```json
{
  "success": true,
  "message": "Course updated successfully.",
  "data": { "id": "course_201", "title": "Linear Algebra II", "description": "Eigenvalues and SVD", "ownerId": "user-b" }
}
```

**Errors:** `400`, `401`, `403` (another student's course), `404`.

---

### `DELETE /api/v1/courses/{id}` — Delete a course

**Path parameters:** `id` — course ID.

**Success — `200 OK`**

```http
DELETE /api/v1/courses/course_102
Authorization: Bearer user-a-token
```

```json
{ "success": true, "message": "Course deleted successfully.", "data": null }
```

**Errors:** `401`, `403`, `404` (including deleting the same course twice).
