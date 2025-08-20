# app/models/user.py

from typing import Optional
from enum import StrEnum
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Boolean, Column, DateTime, func
from pydantic import EmailStr


class Role(StrEnum):
    """
    Defines user roles for access control and permission management.
    """

    USER = "USER"
    ADMIN = "ADMIN"


class UserBase(SQLModel):
    """
    Base user model representing core user details and account status.
    """

    __tablename__ = "app_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr
    name: Optional[str] = None
    # If user's account is deactivated (by choice or system penalty)
    is_enabled: bool = Field(default=True, nullable=False)
    # True when user verifies email
    is_verified: bool = Field(
        default=False,
        nullable=False,
    )
    # True when user requests account deletion, Login can remove account deletion flag
    is_deleted: bool = Field(
        sa_column=Column(Boolean, nullable=False, server_default="false")
    )


class User(UserBase, table=True):
    """
    User model extending UserBase with authentication, role, and audit timestamps.

    Enforces immutability of `created_at` at the model level.
    """

    hashed_password: str
    role: Role = Role.USER
    verification_code: Optional[str] = None
    verification_code_expires_at: Optional[datetime] = None

    pets: list["Pet"] = Relationship(back_populates="owner", cascade_delete=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),  # PostgreSQL DB time config must be set to UTC
            server_default=func.now(),
            onupdate=func.now(),
        )
    )
    last_login_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    def __setattr__(self, name, value) -> None:
        """
        Prevent update for `created_at` field.
        NOTE: Ultimate protection should be enforced in the DB.
        """
        # Allow setting 'created_at' during initialization
        if name == "created_at" and getattr(self, "_initialized", False):
            raise AttributeError("created_at is immutable")
        super().__setattr__(name, value)

    def __post_init__(self):
        self._initialized = True


# Resolve forward references after both classes are defined
from app.models.pet import Pet

User.model_rebuild()
