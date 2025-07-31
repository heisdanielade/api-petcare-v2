# app/services/user_service.py

from typing import Any

from app.models.user import User


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
    user_initial = current_user.name[0].upper(
    ) if current_user.name else current_user.email[0].upper()

    data = {
        "email": current_user.email,
        "name": current_user.name,
        "initial": user_initial,
        "role": current_user.role,
        "is_verified": current_user.is_verified
    }

    return data
