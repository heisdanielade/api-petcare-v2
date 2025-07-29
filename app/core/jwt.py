# app/core/jwt.py

from datetime import datetime, timezone, timedelta
from typing import Any, Union

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings

ALGORITHM = "HS256"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY,  # type: ignore
                             algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) from e


def create_access_token(data: dict[str, Union[str, int]]):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(seconds=settings.JWT_EXPIRATION_TIME)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
