
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlmodel import SQLModel

from app.api.routes import health
from app.api.routes import auth
from app.utils.response import standard_response
from app.db.session import engine


# Create DB
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

# Routers
app.include_router(health.router)
app.include_router(auth.router)


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


@app.get("/")
def read_root() -> dict[str, Any]:
    """Sample base endpoint."""
    return standard_response("success", "Welcome to PetCare API!")
