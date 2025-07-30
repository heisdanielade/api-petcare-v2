# app/api/routes/user.py

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.utils.response import standard_response
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_current_user_details(current_user: User = Depends(get_current_user)) -> dict[str, Any]:

    user_initial = current_user.name[0].upper(
    ) if current_user.name else current_user.email[0].upper()

    data = {
        "email": current_user.email,
        "name": current_user.name,
        "initial": user_initial,
        "role": current_user.role,
        "is_verified": current_user.is_verified
    }

    return standard_response(
        status="success",
        message="User details retrieved successfully",
        data=data)
