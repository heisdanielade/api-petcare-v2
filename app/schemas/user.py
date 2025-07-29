# app/schemas/user.py

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserVerify(BaseModel):
    email: str
    verification_code: str
