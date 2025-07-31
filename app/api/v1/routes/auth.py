# app/api/routes/auth.py

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.user import UserCreate
from app.schemas.auth import VerifyEmailRequest, LoginRequest, ResendVerificationEmailRequest
from app.services.auth_service import register_new_user, verify_new_user_email, login_existing_user, resend_verification_email_to_user
from app.utils.response import standard_response


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Register a new user account.

    Accepts user registration details including email and password.
    Returns a success message prompting the user to verify their email.

    Args:
        user_create (UserCreate): User registration details.

    Returns:
        dict(str, Any): Success message instructing the user to check their email.

    Raises:
        HTTPException: 409 Conflict if the email is already registered.
    """

    await register_new_user(user_create=user_create, db=db)

    return standard_response(
        status="success",
        message="Registration successful. Please check your email to verify your account"
    )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(user_verify: VerifyEmailRequest, db: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Endpoint to verify a user's email address.

    Accepts the user's email and verification code, verifies the code,
    and activates the user account. Returns a success message upon completion.

    Args:
        user_verify (VerifyEmailRequest): User's email and verification code.
        db (Session): SQLModel session injected by dependency.

    Returns:
        dict(str, Any): Success message confirming email verification.

    Raises:
        HTTPException: 404 Not Found if the user account does not exist.
        HTTPException: 409 Conflict if the account is already verified.
        HTTPException: 400 Bad Request if the verification code is invalid or expired.
    """
    await verify_new_user_email(user_verify=user_verify, db=db)

    return standard_response(status="success", message="Email verified successfully")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data: LoginRequest, db: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Authenticate a user and issue an access token.

    Accepts user login credentials and returns a JWT token upon successful authentication.

    Args:
        data (LoginRequest): User login credentials including email and password.

    Returns:
        dict(str, Any): Success message with access token and token details.

    Raises:
        HTTPException: 401 Unauthorized if login credentials are invalid.
        HTTPException: 403 Forbidden if the user account is unverified.
    """
    response = await login_existing_user(login_request=data, db=db)

    return standard_response(
        status="success",
        message="Login successful",
        data=response
    )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification_email(request: ResendVerificationEmailRequest, db: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Resend a verification email to a user.

    Accepts the user's email and triggers sending of a new verification email if applicable.

    Args:
        request (ResendVerificationEmailRequest): Email address to resend the verification code to.

    Returns:
        dict(str, Any): Success message indicating that the verification email has been sent.
    """
    await resend_verification_email_to_user(request=request, db=db)

    return standard_response(
        status="success",
        message="Verification email sent successfully"
    )
