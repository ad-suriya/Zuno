"""Consistent error responses.

Every error body is: {"error": {"code": str, "message": str, "request_id": str | null}}
Internal details are logged, never returned to the client.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from google.api_core import exceptions as gcp_exceptions
from google.auth.exceptions import DefaultCredentialsError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.repository import ConflictError, NotFoundError

log = logging.getLogger("zuno.errors")

STORAGE_ERRORS = (gcp_exceptions.GoogleAPIError, DefaultCredentialsError)


class ApiProblem(Exception):
    """An expected failure with a stable error code, e.g. VOICE_UNAVAILABLE (503) or TOO_LARGE (413)."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def error_response(request: Request, status: int, code: str, message: str) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "request_id": request_id}},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found(request: Request, exc: NotFoundError):
        return error_response(request, 404, "NOT_FOUND", f"{exc.what} not found.")

    @app.exception_handler(ApiProblem)
    async def api_problem(request: Request, exc: ApiProblem):
        return error_response(request, exc.status, exc.code, exc.message)

    @app.exception_handler(ConflictError)
    async def conflict(request: Request, exc: ConflictError):
        return error_response(request, 409, "CONFLICT", str(exc))

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError):
        # Report which fields failed, not the submitted values (they may contain user content).
        fields = sorted({".".join(str(p) for p in e["loc"] if p != "body") for e in exc.errors()})
        return error_response(request, 422, "VALIDATION_ERROR", f"Invalid request: {', '.join(fields)}.")

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return error_response(request, exc.status_code, "HTTP_ERROR", str(exc.detail))

    async def storage_unavailable(request: Request, exc: Exception):
        log.error("storage_error", exc_info=exc, extra={"request_id": getattr(request.state, "request_id", None)})
        return error_response(request, 503, "STORAGE_UNAVAILABLE", "Storage is temporarily unavailable. Try again.")

    for exc_type in STORAGE_ERRORS:
        app.add_exception_handler(exc_type, storage_unavailable)

    # Unhandled exceptions become 500s in the request middleware (app/main.py).
