# app/models/user.py

from typing import Optional
from enum import StrEnum
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserBase(SQLModel):
    __tablename__ = "app_user"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr
    name: Optional[str] = None
    enabled: bool = False  # Until user verifies email


class User(UserBase, table=True):
    hashed_password: str
    role: Role = Role.USER
    verification_code: Optional[str] = None
    verification_code_expires_at: Optional[datetime] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
