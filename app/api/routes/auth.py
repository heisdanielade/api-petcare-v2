# app/api/routes/auth.py

import random
from typing import Any
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Register a new user in the system.

    This endpoint creates a new user account with the provided email and password.
    The password should meet security requirements (e.g., minimum length, complexity).
    On success, returns a message to proceed to email verification.

    Args:
        user (UserRegister): A JSON body containing username, email, and password fields.

    Returns:
        dict: A success message confirming user registration.

    Raises:
        HTTPException 400: If the username or email is already taken or if input validation fails.
    """
    # Check if user already exists
    existing_user = session.exec(select(User).where(
        User.email == user_create.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already exists")

    verification_code = f"{random.randint(100000, 999999)}"  # Six-digit code
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

    # TODO: send verification email with verification_code here

    return {"msg": "Registration successful. Please check your email to verify your account."}
