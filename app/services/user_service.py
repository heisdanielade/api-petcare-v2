# app/services/user_service.py

from typing import Any
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.user import User
from app.services.email_service import EmailService
from app.utils.helpers import generate_verification_code


class UserService:
    @staticmethod
    async def get_current_user_details(current_user: User) -> dict[str, Any]:
        """
        Prepare and return profile details of the authenticated user.

        Extracts key user information such as email, name, role, verification status, and the user's initial
        (from their name or email). Formats this data into a dictionary for response use.

        Args:
            current_user (User): User model instance representing the authenticated user.

        Returns:
            dict(str, Any): Dictionary containing user's email, name, initial, role, and verification status.
        """
        user_initial = (
            current_user.name[0].upper()
            if current_user.name
            else current_user.email[0].upper()
        )

        data = {
            "email": current_user.email,
            "name": current_user.name,
            "initial": user_initial,
            "role": current_user.role,
            "is_verified": current_user.is_verified,
        }

        return data

    @staticmethod
    async def request_account_deletion(user: User, db: Session) -> None:
        """
        Generate a verification code and initiate account deletion process for a user.

        Checks if the user has already scheduled account deletion. If not, generates a
        time-limited verification code and updates the user record in the database.
        Sends an email containing the verification code to the user's registered email.

        Args:
            user (User): The user requesting account deletion.
            db (Session): SQLModel session used to perform database operations.

        Raises:
            HTTPException: 409 Conflict if the account is already scheduled for deletion.
        """
        stmt = select(User).where(User.id == user.id)
        existing_user = db.exec(stmt).one()

        if existing_user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account already scheduled for deletion",
            )

        ver_code = generate_verification_code()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=10
        )  # Valid for 10 minutes

        existing_user.verification_code = ver_code
        existing_user.verification_code_expires_at = expires_at

        db.add(existing_user)
        db.commit()
        db.refresh(existing_user)  # Ensure updated fields are synced

        await EmailService.send_account_deletion_email(
            email_to=existing_user.email, verification_code=ver_code
        )

    @staticmethod
    async def schedule_account_deletion(
        user: User, verification_code: str, db: Session
    ) -> None:
        """
        Verify the account deletion code and schedule the user's account for deletion.

        Checks if the account is already scheduled for deletion. Validates the provided
        verification code against the user's current code and its expiration. If valid,
        marks the account as deleted, clears the verification code, and commits the changes
        to the database. Sends a confirmation email notifying the user that the account
        deletion has been scheduled.

        Args:
            user (User): The user requesting account deletion.
            verification_code (str): The one-time code sent to the user's email.
            db (Session): SQLModel session used to perform database operations.

        Raises:
            HTTPException: 409 Conflict if the account is already scheduled for deletion.
            HTTPException: 400 Bad Request if the verification code is invalid or expired.
        """
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account already scheduled for deletion",
            )

        # Make expires_at timezone-aware
        expires_at = user.verification_code_expires_at
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if (
            user.verification_code != verification_code
            or not user.verification_code_expires_at
            or expires_at < datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code",
            )

        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        user.verification_code = None
        user.verification_code_expires_at = None

        db.add(user)
        db.commit()

        await EmailService.send_account_deletion_scheduled_email(email_to=user.email)
