# StudyPoint API

Backend REST API prototype for **StudyPoint**, an AI-powered study assistant that helps students organize courses and study materials.

This prototype uses **Python and FastAPI**, with mocked data instead of a database.

## Requirements

- Python 3
- Git

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd studypoint-api
```

Replace `<repository-url>` with the repository's GitHub URL.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

On Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Running the API

From the repository root, with the virtual environment activated:

```bash
uvicorn app.main:app --reload
```

The API will run at:

http://127.0.0.1:8000

Interactive API documentation (Swagger UI):

http://127.0.0.1:8000/docs

Press `Ctrl + C` in the terminal to stop the server.
