# app/api/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.db.session import get_session
from app.models.user import User
from app.core.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    user: User = session.get(User, int(user_id))  # type: ignore
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found")
    return user


def check_verified_user(user: User = Depends(get_current_user)):
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Account is unverified, kindly verify your email")
    return user
