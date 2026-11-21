from fastapi import FastAPI

from app.courses import router as courses_router
from app.greeting import router as greeting_router
from app.errors import register_exception_handlers

app = FastAPI(
    title="StudyPoint API",
    description="Mock REST API for the StudyPoint study assistant.",
    version="1.0.0"
)

register_exception_handlers(app)

app.include_router(courses_router)
app.include_router(greeting_router)
