# StudyPoint API

A mock REST API prototype for **StudyPoint**, an AI-powered study assistant that helps students organize courses and study materials.

Built with Python and FastAPI for a Software Engineering assignment.

## Requirements

- Python 3
- Git

## Installation

Clone the repository:

```bash
git clone https://github.com/Grace-Evergarden/studypoint-api.git
cd studypoint-api
```

Create a virtual environment:

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the API

Start the server:

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

- **Interactive documentation:** http://127.0.0.1:8000/docs
- **HTML greeting page:** http://127.0.0.1:8000/api/v1/greeting
- **API reference:** [docs/API.md](docs/API.md)
- **Example requests:** [examples/requests.http](examples/requests.http)

Press `Ctrl+C` to stop the server.

**Note:** The application uses in-memory mock data. Changes to courses are not persistent and will be lost when the server restarts.

## Authentication

The course endpoints require a bearer token.

| Token | Access |
|---|---|
| `user-a-token` | Student A's courses |
| `user-b-token` | Student B's courses |
| `admin-token` | All courses |

Use the `Authorization` header:

```http
Authorization: Bearer user-a-token
```

The greeting endpoint does not require authentication.

## Testing

Run all automated tests:

```bash
python -m pytest -v
```

## Contributors

StudyPoint API was developed by **Group 9**.

| Contributor | Implementation |
|---|---|
| **Ziyaddin Musayev** | `app/courses.py`, `app/store.py`, `tests/test_courses.py`, `docs/API.md`, `examples/requests.http` |
| **Kamran Gulmammedov** | `app/auth.py`, `app/schemas.py`, `app/errors.py`, `tests/test_auth.py`, `tests/test_validation.py` |
| **Elyar Nuraliyev (Grace)** | `app/main.py`, `app/greeting.py`, `app/templates/greeting.html`, `tests/test_greeting.py`, `README.md`, `CONTRIBUTORS.md` |

For student IDs, responsibilities, and collaboration details, see [CONTRIBUTORS.md](CONTRIBUTORS.md).

### Git Contributions

Output of `git shortlog -sn --all`:

```text
14  Grace
 5  Elyar
 5  ZiyaddinMusayev001
 1  Кемран Гульмомедов
```

**Note:** `Grace` and `Elyar` are two Git author names used by the same contributor.

## Demonstration

YouTube video: https://youtu.be/t75_FGTHkZQ
