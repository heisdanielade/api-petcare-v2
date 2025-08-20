# app/api/routes/user.py

from typing import Any

from fastapi import Request, APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.models.user import User
import app.schemas.user as user_schemas
from app.core.rate_limiter import limiter
from app.utils.response import standard_response
from app.api.dependencies import get_current_user
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def user_info(
    request: Request, current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Retrieve the currently authenticated user's profile details.

    Returns basic information about the logged-in user including email, name, role, and verification status.

    Args:
        current_user (User): The authenticated user obtained from the request context.

    Returns:
        dict(str, Any): Success message with the user's profile details.

    Raises:
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    response = await UserService.get_current_user_details(current_user=current_user)

    return standard_response(
        status="success", message="User details retrieved successfully", data=response
    )


@router.get("/delete/request-otp", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def request_account_deletion(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Request a verification code for account deletion.

    Sends a one-time verification code to the email of the currently authenticated user.
    The code is required to confirm account deletion.

    Args:
        current_user (User): The authenticated user making the request.

    Returns:
        dict(str, Any): Success message indicating that the verification code has been sent.

    Raises:
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await UserService.request_account_deletion(user=current_user, db=db)

    return standard_response(
        status="success", message="Verification code sent successfully"
    )


@router.post("/delete/verify-otp", status_code=200)
@limiter.limit("2/minute")
async def delete_account(
    request: Request,
    req_data: user_schemas.UserDeleteScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Schedule the deletion of the authenticated user's account.

    Verifies the provided one-time code and, if valid, schedules the user's account
    for deletion.

    Args:
        req_data (UserDeleteScheduleRequest): Contains the verification code sent to the user's email.
        current_user (User): The authenticated user requesting account deletion.

    Returns:
        dict(str, Any): Success message confirming that the account has been scheduled for deletion.

    Raises:
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
        HTTPException: 400 Bad Request if the verification code is invalid or expired.
    """

    await UserService.schedule_account_deletion(
        user=current_user, verification_code=req_data.verification_code, db=db
    )

    return standard_response(
        status="success", message="Account has been scheduled for deletion"
    )
