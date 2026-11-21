from fastapi import FastAPI
from app.greeting import router as greeting_router

app = FastAPI(
    title="StudyPoint API",
    description="Mock REST API for the StudyPoint study assistant.",
    version="1.0.0"
)

app.include_router(greeting_router)
