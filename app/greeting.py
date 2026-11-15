from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML_FILE = Path(__file__).resolve().parent / "templates" / "greeting.html"


@router.get("/api/v1/greeting", response_class=HTMLResponse)
def greeting():
    return HTMLResponse(
        content=HTML_FILE.read_text(encoding="utf-8"),
        media_type="text/html"
    )
