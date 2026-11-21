"""Standard JSON response helpers and application-wide exception handlers."""
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

_ERROR_CODES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
}


def success_response(
    message: str,
    data: Any,
    status_code: int = 200,
    meta: dict | None = None,
) -> JSONResponse:
    """Build the shared success envelope used by JSON endpoints."""
    body: dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        body["meta"] = meta
    return JSONResponse(status_code=status_code, content=body)


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: list | None = None,
) -> JSONResponse:
    """Build the shared error envelope; details are included only when supplied."""
    error: dict[str, Any] = {"code": code, "message": message}
    if code == "VALIDATION_ERROR" and details is not None:
        error["details"] = details
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": error},
    )


async def _validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = []
    for item in exc.errors():
        location = item.get("loc", ())
        
        field_parts = [str(part) for part in location if part not in ("body", "query", "path")]
        field = ".".join(field_parts) or "request"
        details.append({"field": field, "message": item.get("msg", "Invalid value.")})
    return error_response(
        400,
        "VALIDATION_ERROR",
        "The request contains invalid or missing fields.",
        details,
    )


async def _http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code = _ERROR_CODES.get(exc.status_code)
    if code is None:
        code = "INTERNAL_ERROR" if exc.status_code >= 500 else "VALIDATION_ERROR"
    message = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
    return error_response(exc.status_code, code, message)


async def _unexpected_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.exception("Unhandled application error", exc_info=exc)
    return error_response(
        500,
        "INTERNAL_ERROR",
        "An unexpected server error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers so FastAPI/Pydantic errors use the agreed JSON envelope."""
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _unexpected_exception_handler)