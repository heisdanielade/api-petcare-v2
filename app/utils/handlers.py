# app/utils/handlers.py

from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.response import standard_response


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Return original response for api docs authentication
    if exc.status_code == 401 and exc.headers is not None and "WWW-Authenticate" in exc.headers:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    # Otherwise
    return JSONResponse(
        status_code=exc.status_code,
        content=standard_response(
            status="error",
            message=exc.detail,
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Clean exc.errors() to remove exception objects in 'ctx'
    def sanitize_error(err: dict[str, Any]) -> dict[str, Any]:
        sanitized = err.copy()
        if "ctx" in sanitized:
            sanitized["ctx"] = {
                k: (str(v) if isinstance(v, Exception) else v)
                for k, v in sanitized["ctx"].items()
            }
        return sanitized

    clean_errors = [sanitize_error(e) for e in exc.errors()]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=standard_response(
            status="error",
            message="Input validation failed",
            data={"errors": clean_errors}
        )
    )


async def internal_server_error_handler(request: Request, exc: Exception):
    # TODO: log the stack trace

    return JSONResponse(
        status_code=500,
        content=standard_response(
            status="error",
            message="Unexpected error occured",
        )
    )
