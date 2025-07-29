# app/api/routes/health.py

from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies import check_enabled_user
from app.utils.response import standard_response

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", dependencies=[Depends(check_enabled_user)])
# @router.get("/")
def health_check() -> dict[str, Any]:
    return standard_response("success", "All services are active.")
