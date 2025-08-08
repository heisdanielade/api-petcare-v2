# app/main.py
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.routes import health
from app.api.v1.routes import auth
from app.api.v1.routes import user

import app.utils.handlers as handler
from app.utils.response import standard_response
from app.core.config import settings


app = FastAPI()

origins = [
    settings.FRONTEND_DEV_URL,  # frontend dev URL
    settings.FRONTEND_PROD_URL,  # frontend prod URL
]

# Middlewares
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


# Exception handlers
app.add_exception_handler(
    StarletteHTTPException,
    handler.http_exception_handler)  # type: ignore
app.add_exception_handler(
    RequestValidationError,
    handler.validation_exception_handler)  # type: ignore
app.add_exception_handler(
    Exception, handler.internal_server_error_handler)


@app.get("/")
def read_root() -> dict[str, Any]:
    """Sample base endpoint."""
    return standard_response("success", "Welcome to PetCare API!")
