# app/api/routes/user.py

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.utils.response import standard_response
from app.api.dependencies import get_current_user
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", status_code=status.HTTP_200_OK)
async def user_info(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """
    Retrieve the currently authenticated user's profile details.

    Returns basic information about the logged-in user including email, name, role, and verification status.

    Args:
        current_user (User): The authenticated user obtained from the request context.

    Returns:
        dict(str, Any): Success message with the user's profile details.
    """
    response = await UserService.get_current_user_details(current_user=current_user)

    return standard_response(
        status="success", message="User details retrieved successfully", data=response
    )
