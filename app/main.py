
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
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
    return JSONResponse(
        status_code=422,
        content=standard_response(
            status="error",
            message="Validation failed",
            data={"errors": exc.errors()}
        )
    )


@app.get("/")
def read_root() -> dict[str, Any]:
    """Sample base endpoint."""
    return standard_response("success", "Welcome to PetCare API!")
