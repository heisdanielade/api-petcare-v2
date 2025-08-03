# app/core/jwt.py

from datetime import datetime, timezone, timedelta
from typing import Any, Union

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings

ALGORITHM = "HS256"


def decode_token(token: str) -> dict[str, Any]:
    """Decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY,  # type: ignore
            algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token"
        ) from e


def create_access_token(data: dict[str, Union[str, int]]):
    """
    Create login access token.
    Valid for 3 days.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(seconds=settings.JWT_EXPIRATION_TIME)
    to_encode.update({"exp": expire})  # type: ignore
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY,  # type: ignore
        algorithm=ALGORITHM)


def create_password_reset_token(email: str):
    """
    Create Password reset token.
    Valid for 15 minutes.
    """
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=15)  # Valid for 15 minutes
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "password_reset"
    }

    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY,  # type: ignore
        algorithm=ALGORITHM)
