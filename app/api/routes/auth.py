# app/api/routes/auth.py

import random
import string
from typing import Any
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import VerifyEmailRequest, LoginRequest, TokenResponse
from app.utils.response import standard_response
from app.core.security import hash_password, verify_password
from app.services import email_service as es
from app.core.jwt import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def generate_verification_code(length: int = 6):
    return ''.join(random.choices(string.digits, k=length))


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Register a new user in the system.

    This endpoint creates a new user account with the provided email and password.
    The password should meet security requirements (e.g., minimum length, complexity).
    On success, returns a message to proceed to email verification.

    Args:
        user (UserCreate): A JSON body containing email and password fields.

    Returns:
        dict: A success message confirming user to proceed to email verification.

    Raises:
        HTTPException 409: If the email is already taken.
    """
    # Check if user already exists
    existing_user = db.exec(select(User).where(
        User.email == user_create.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already exists")

    # Verification code to be sent yo user email to enable user's account
    verification_code = generate_verification_code()
    expires_at = datetime.now(timezone.utc) + \
        timedelta(minutes=10)  # Valid for 10 minutes

    user: User = User(
        email=user_create.email,
        hashed_password=hash_password(user_create.password),
        verification_code=verification_code,
        verification_code_expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    await es.send_verification_email(email_to=user.email, code=verification_code)

    return standard_response(status="success", message="Registration successful. Please check your email to verify your account.")


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(user_verify: VerifyEmailRequest, db: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Verify user email.

    This endpoint verifies a user's account with the provided email and verification code that
    is sent to the user's email.
    On success, returns a verification sucessful message.

    Args:
        user_email: Email address of user's account to be verified.
        verification_code: Six-digit numeric code sent to user's email.

    Returns:
        dict: A success message confirming that the user's email has been verified.

    Raises:
        HTTPException 400: If the verification code is invalid or expired.
        HTTPException 404: If the user's account (email) is not found in the system.
    """
    stmt = select(User).where(User.email == user_verify.email)
    user = db.exec(stmt).one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Account does not exist")

    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already verified")

    # Make expires_at timezone-aware
    expires_at = user.verification_code_expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Check code matches and is not expired
    if (user.verification_code != user_verify.verification_code or not user.verification_code_expires_at or expires_at < datetime.now(timezone.utc)):  # type: ignore
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid or expired verification code.")

    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None

    db.add(user)
    db.commit()

    await es.send_welcome_email(email_to=user.email)

    return standard_response(status="success", message="Email verified successfully.")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data: LoginRequest, db: Session = Depends(get_session)):
    """
    Login user.

    This endpoint verifies a user's credentials to login with a provided email and password.
    Checks that user.is_verified == True.
    On success, returns a JWT access token.

    Args:
        email (from LoginRequest): Email address of user.
        password (from LoginRequest): Plane password gotten from user.

    Returns:
        dict: A success message with JWT access token.

    Raises:
        HTTPException 400: If the provided login credentials are invalid.
        HTTPException 403: If the user's account (email) is not verified.
    """
    stmt = select(User).where(User.email == data.email)
    user = db.exec(stmt).one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login credentials")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Account is unverified, kindly verify your email")

    expire = datetime.now(timezone.utc) + \
        timedelta(seconds=settings.JWT_EXPIRATION_TIME)
    access_token = create_access_token({"sub": user.email})

    return standard_response(
        status="success",
        message="Login successful",
        data={
            "token": access_token,
            "type": "bearer",
            "expires_at": expire.isoformat()
        }
    )
