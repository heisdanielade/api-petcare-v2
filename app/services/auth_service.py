# app/services/auth_service.py

import random
import string
from typing import Any
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.user import User
from app.core.security import hash_password, verify_password
from app.core.config import settings
import app.schemas.auth as auth_schemas
import app.schemas.user as user_schemas
from app.services.email_service import EmailService
from app.core.jwt import create_access_token, create_password_reset_token, decode_token


class AuthService:
    @staticmethod
    def generate_verification_code(length: int = 6):
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    async def register_new_user(user_create: user_schemas.UserCreate, db: Session) -> None:
        """
        Register a new user in the database and initiate email verification.

        Checks if a user with the provided email already exists. If not, creates a new user record
        with a hashed password and a verification code valid for a limited time. Sends a verification
        email containing the code to the user's email address.

        Args:
            user_create (UserCreate): Pydantic model containing the user's email and password.
            db (Session): SQLModel session used to perform database operations.

        Raises:
            HTTPException: 409 Conflict if a user with the given email already exists.
        """
        # Check if user already exists
        existing_user = db.exec(select(User).where(
            User.email == user_create.email)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Account already exists")

        # Verification code to be sent yo user email to enable user's account
        verification_code = AuthService.generate_verification_code()
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
        db.add(user)
        db.commit()
        db.refresh(user)

        await EmailService.send_verification_email(email_to=user.email, code=verification_code)

    @staticmethod
    async def verify_user_email(user_verify: auth_schemas.VerifyEmailRequest, db: Session) -> None:
        """
        Verify a user's email address using a verification code.

        Checks if the user exists and is not already verified. Validates that the
        provided verification code matches and is not expired. Upon successful
        verification, marks the user as verified and sends a welcome email.

        Args:
            user_verify (VerifyEmailRequest): Pydantic model containing user's email and verification code.
            db (Session): SQLModel session for database operations.

        Raises:
            HTTPException: 404 Not Found if the user account does not exist.
            HTTPException: 409 Conflict if the account is already verified.
            HTTPException: 400 Bad Request if the verification code is invalid or expired.
        """
        stmt = select(User).where(User.email == user_verify.email)
        user = db.exec(stmt).one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Account does not exist")

        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Account already verified")

        # Make expires_at timezone-aware
        expires_at = user.verification_code_expires_at
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Check code matches and is not expired
        if (user.verification_code != user_verify.verification_code or not user.verification_code_expires_at or expires_at < datetime.now(timezone.utc)):  # type: ignore
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid or expired verification code")

        user.is_verified = True
        user.verification_code = None
        user.verification_code_expires_at = None

        db.add(user)
        db.commit()

        await EmailService.send_welcome_email(email_to=user.email)

    @staticmethod
    async def login_existing_user(login_request: auth_schemas.LoginRequest, db: Session) -> dict[str, Any]:
        """
        Authenticate an existing user and generate a JWT access token.

        Queries the database for a user matching the provided email. Verifies the provided password
        against the stored hashed password. Checks if the user account is verified. If authentication
        is successful, generates a JWT token with an expiration time.

        Args:
            login_request (LoginRequest): Pydantic model containing user email and password.
            db (Session): SQLModel session used for database queries.

        Returns:
            dict(str, Any): Dictionary containing the JWT token, token type, and expiry datetime.

        Raises:
            HTTPException: 401 Unauthorized if the email does not exist or password is incorrect.
            HTTPException: 403 Forbidden if the user account is not verified.
        """
        stmt = select(User).where(User.email == login_request.email)
        user = db.exec(stmt).one_or_none()

        if not user or not verify_password(login_request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login credentials")

        if not user.is_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Account is unverified, kindly verify your email")

        expire = datetime.now(timezone.utc) + \
            timedelta(seconds=settings.JWT_EXPIRATION_TIME)
        access_token = create_access_token({"sub": user.email})

        return {
            "token": access_token,
            "type": "bearer",
            "expiry": expire,
        }

    @staticmethod
    async def resend_verification_email(request: auth_schemas.ResendVerificationEmailRequest, db: Session) -> None:
        """
        Generate and send a new email verification code to the user.

        Creates a new verification code and dispatches it to the specified email address.

        Args:
            request (ResendVerificationEmailRequest): Pydantic model containing the user's email.
            db (Session): SQLModel session used for potential database interactions.
        """
        stmt = select(User).where(User.email == request.email)
        existing_user = db.exec(stmt).one_or_none()

        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Account does not exist")

        if existing_user.is_verified:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Account is already verified")

        code = AuthService.generate_verification_code()
        expires_at = datetime.now(timezone.utc) + \
            timedelta(minutes=10)  # Valid for 10 minutes

        existing_user.verification_code = code
        existing_user.verification_code_expires_at = expires_at
        existing_user.updated_at = datetime.now(timezone.utc)

        db.add(existing_user)
        db.commit()

        await EmailService.send_verification_email(email_to=existing_user.email, code=code)

    @staticmethod
    async def request_password_reset(request: auth_schemas.PasswordResetLinkRequest, db: Session) -> None:
        """
        Send a password reset email with a reset link to the user.

        Generates a password reset token, then sends a reset email that includes a reset link based on the generated token to the specified email address.

        Args:
            request (PasswordResetLinkRequest): Pydantic model containing the user's email.
            db (Session): SQLModel session used for potential database interactions.
        """
        stmt = select(User).where(User.email == request.email)
        existing_user = db.exec(stmt).one_or_none()

        if not existing_user or not existing_user.is_verified:
            ...  # To prevent email enumeration attack, do nothing
        reset_token = create_password_reset_token(request.email)

        await EmailService.send_password_reset_email(email_to=existing_user.email, reset_token=reset_token)

    @staticmethod
    async def reset_user_password(token: str, new_password: str, db: Session) -> None:
        """
        Send a password reset email with a reset link to the user.

        Generates a password reset token, then sends a reset email that includes a reset link based on the generated token to the specified email address.

        Args:
            token: A JWT for password reset.
            new_password: New user's password.
            db (Session): SQLModel session used for potential database interactions.
        """
        payload = decode_token(token)
        user_email = payload.get("sub")

        stmt = select(User).where(User.email == user_email)
        existing_user = db.exec(stmt).one_or_none()

        hashed_password = hash_password(new_password)

        now = datetime.now(timezone.utc)
        existing_user.hashed_password = hashed_password  # type: ignore
        existing_user.updated_at = now  # type: ignore

        # User-friendly time format
        reset_time = now.strftime('%Y-%m-%d %H:%M:%S UTC')

        db.add(existing_user)
        db.commit()

        await EmailService.send_password_reset_notification_email(email_to=existing_user.email, reset_time=reset_time)
