# app/schemas/auth.py

from pydantic import BaseModel, EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    verification_code: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
