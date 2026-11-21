"""Pydantic request/response schemas shared by the StudyPoint API."""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CourseCreate(BaseModel):
    """Fields accepted when creating a course; ownership and ID are server-set."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(default="", max_length=500)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Title must be 3–100 characters after trimming.")
        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return value.strip()


class CourseUpdate(CourseCreate):
    """Fields accepted by PUT; same editable fields as course creation."""


class CourseResponse(BaseModel):
    id: str
    title: str
    description: str = ""
    ownerId: str


class PaginationMeta(BaseModel):
    total: int
    page: int
    perPage: int


class SuccessEnvelope(BaseModel):
    success: bool = True
    message: str
    data: Any
    meta: PaginationMeta | None = None


class ValidationDetail(BaseModel):
    field: str
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ValidationDetail] | None = None


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorBody
