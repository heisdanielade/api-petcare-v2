# app/api/routes/health.py

from typing import Any

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import check_verified_user
from app.utils.response import standard_response
from app.db.session import engine
router = APIRouter()


# @router.get("/", dependencies=[Depends(check_verified_user)])
@router.get("/")
def health_check() -> dict[str, Any]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        # TODO: add logging
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        ) from e

    return standard_response("success", "All services are active.")
