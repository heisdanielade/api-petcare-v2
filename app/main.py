# app/main.py

import time
from typing import Any

from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from slowapi.errors import RateLimitExceeded

from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from app.api.v1.routes import health
from app.api.v1.routes import auth
from app.api.v1.routes import user

from app.core.logging import log_requests
from app.core.rate_limiter import limiter
import app.utils.handlers as handler
from app.utils.response import standard_response
from app.core.config import settings
from app.api.dependencies import authenticate


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.state.limiter = limiter

origins = [
    settings.FRONTEND_DEV_URL,  # frontend dev URL
    settings.FRONTEND_PROD_URL,  # frontend prod URL
]

# Middlewares
app.middleware("http")(log_requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(health.router, prefix="/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/v1/user", tags=["user"])


# Exception handlers
app.add_exception_handler(RateLimitExceeded, handler.rate_limit_handler)  # type: ignore
app.add_exception_handler(StarletteHTTPException, handler.http_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, handler.validation_exception_handler)  # type: ignore
app.add_exception_handler(Exception, handler.internal_server_error_handler)


# Routes for API docs
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui(authenticated: bool = Depends(authenticate)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_ui(authenticated: bool = Depends(authenticate)):
    return get_redoc_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(authenticated: bool = Depends(authenticate)):
    return get_openapi(title="My API", version="1.0.0", routes=app.routes)


@app.get("/")
def read_root() -> dict[str, Any]:
    """Sample base endpoint."""
    return standard_response("success", "Welcome to PetCare API!")
