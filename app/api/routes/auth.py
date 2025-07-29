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
from app.utils.response import standard_response
from app.core.security import hash_password
from app.services import email_service as es

router = APIRouter(prefix="/auth", tags=["auth"])


def generate_verification_code(length: int = 6):
    return ''.join(random.choices(string.digits, k=length))


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
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
    existing_user = session.exec(select(User).where(
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

    session.add(user)
    session.commit()
    session.refresh(user)

    await es.send_verification_email(email_to=user.email, code=verification_code)

    return standard_response(status="success", message="Registration successful. Please check your email to verify your account.")


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(user_email: str, verification_code: str, session: Session = Depends(get_session)) -> dict[str, Any]:
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
    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Account does not exist")

    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already verified")

    # Check code matches and is not expired
    if (user.verification_code != verification_code or not user.verification_code_expires_at or user.verification_code_expires_at < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid or expired verification code.")

    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None

    session.add(user)
    session.commit()

    return standard_response(status="success", message="Email verified successfully.")
