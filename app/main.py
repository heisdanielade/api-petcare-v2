
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

from app.api.routes import health
from app.utils.response import standard_response

app = FastAPI()

# Routers
app.include_router(health.router)


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
