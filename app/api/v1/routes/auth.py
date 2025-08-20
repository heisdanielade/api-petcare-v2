# app/api/routes/auth.py

from typing import Any

from fastapi import Request, APIRouter, Depends, status
from sqlmodel import Session

from app.core.rate_limiter import limiter
from app.db.session import get_session
import app.schemas.auth as auth_schemas
import app.schemas.user as user_schemas
from app.services.auth_service import AuthService
from app.utils.response import standard_response


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def register(
    request: Request,
    user_create: user_schemas.UserCreate,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
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
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """

    await AuthService.register_new_user(user_create=user_create, db=db)

    return standard_response(
        status="success",
        message="Registration successful. Please check your email to verify your account",
    )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def verify_email(
    request: Request,
    user_verify: auth_schemas.VerifyEmailRequest,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
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
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await AuthService.verify_user_email(user_verify=user_verify, db=db)

    return standard_response(status="success", message="Email verified successfully")


@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: auth_schemas.LoginRequest,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
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
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    response = await AuthService.login_existing_user(login_request=data, db=db)

    return standard_response(
        status="success", message="Login successful", data=response
    )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def resend_verification_email(
    request: Request,
    req_data: auth_schemas.ResendVerificationEmailRequest,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Resend a verification email to a user.

    Accepts the user's email and triggers sending of a new verification email if applicable.

    Args:
        request (ResendVerificationEmailRequest): Email address to resend the verification code to.

    Returns:
        dict(str, Any): Success message indicating that the verification email has been sent.

    Raises:
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await AuthService.resend_verification_email(request=req_data, db=db)

    return standard_response(
        status="success", message="Verification email sent successfully"
    )


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def request_password_reset(
    request: Request,
    req_data: auth_schemas.PasswordResetLinkRequest,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Resend a password reset email to a user.

    Accepts the user's email and triggers sending of an email with password reset instructions.

    Args:
        request (PasswordResetLinkRequest): Email address to send the reset email to.

    Returns:
        dict(str, Any): Success message indicating that the password reset email has been sent.

    Raises:
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await AuthService.request_password_reset(request=req_data, db=db)

    return standard_response(
        status="success", message="Password reset email sent successfully"
    )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def reset_password(
    request: Request,
    req_data: auth_schemas.ResetPasswordRequest,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Change the password of a user.

    Accepts the reset token and new password then changes the user's password if the token is valid and user exists.

    Args:
        request (ResetPasswordRequest): A JWT for password reset and the new user's password.

    Returns:
        dict(str, Any): Success message indicating that the user's password has been reset.

    Raises:
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await AuthService.reset_user_password(
        token=req_data.token, new_password=req_data.new_password, db=db
    )

    return standard_response(status="success", message="Password reset successfully")
