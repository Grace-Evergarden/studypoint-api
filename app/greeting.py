from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML_FILE = Path(__file__).resolve().parent / "templates" / "greeting.html"


@router.get(
    "/api/v1/greeting",
    response_class=HTMLResponse,
    tags=["greeting"],
    summary="Display the StudyPoint greeting page",
    description=(
        "Returns a responsive HTML page introducing StudyPoint, "
        "its team members, API endpoints, and running status. "
        "No authentication is required."
    ),
    responses={
    200: {
        "description": "Greeting page returned successfully as HTML.",
        "content": {
            "text/html": {
                "example": (
                    "<!DOCTYPE html>\n"
                    "<html>\n"
                    "  <head><title>StudyPoint API</title></head>\n"
                    "  <body><h1>Welcome to StudyPoint</h1></body>\n"
                    "</html>"
                )
            }
        }
    }
},
)
def greeting():
    return HTMLResponse(
        content=HTML_FILE.read_text(encoding="utf-8"),
        media_type="text/html"
    )
