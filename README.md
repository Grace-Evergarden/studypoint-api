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

Team 9:

| Contributor | Responsibilities |
|---|---|
| Ziyaddin Musayev | CRUD endpoints, mock storage, and tests |
| Kamran Gulmammedov | Authentication, authorization, validation, and error handling |
| Elyar Nuraliyev | Architecture, API contract, application setup, greeting page, documentation, and integration |

Full contributor details: [CONTRIBUTORS.md](CONTRIBUTORS.md).

### Git Contributions

Output of `git shortlog -sn --all`:

```text
[Insert actual command output after final merges]
```

## Demonstration

YouTube video: [Insert demonstration link]
