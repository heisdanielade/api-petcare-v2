# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, field_validator, Field


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    verification_code: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResendVerificationEmailRequest(BaseModel):
    email: EmailStr


class PasswordResetLinkRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    def password_strength(cls, v):
        """Check user password complexity."""
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number.")
        return v
