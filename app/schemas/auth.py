# app/schemas/auth.py

from pydantic import BaseModel, EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    verification_code: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResendVerificationEmailRequest(BaseModel):
    email: EmailStr
