
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.routes import health
from app.api.v1.routes import auth
from app.api.v1.routes import user
from app.utils.response import standard_response
from app.core.config import settings


app = FastAPI()

origins = [
    settings.FRONTEND_DEV_URL,  # frontend dev URL
    settings.FRONTEND_PROD_URL,  # frontend prod URL
]

# Handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # type: ignore
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/v1/user", tags=["user"])


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=standard_response(
            status="error",
            message=exc.detail,
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Clean exc.errors() to remove exception objects in 'ctx'
    def sanitize_error(err):
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
            message="Validation failed",
            data={"errors": clean_errors}
        )
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    # TODO: log the stack trace

    return JSONResponse(
        status_code=500,
        content=standard_response(
            status="error",
            message="An unexpected error occured",
        )
    )


@app.get("/")
def read_root() -> dict[str, Any]:
    """Sample base endpoint."""
    return standard_response("success", "Welcome to PetCare API!")
