# app/models/pet.py

from typing import Optional
from enum import StrEnum
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship


class Sex(StrEnum):
    """
    Enumeration representing biological sex options.
    """

    MALE = "Male"
    FEMALE = "Female"
    NOT_SPECIFIED = "Not Specified"


class Species(SQLModel, table=True):
    """
    Represents a species entry in the taxonomy with a unique code, display name, and optional category.
    """

    __tablename__ = "species"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    name: str
    category: Optional[str] = None


class PetBase(SQLModel):
    """
    Base model for pets, storing basic details such as name, sex, and species reference.
    """

    __tablename__ = "pet"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    sex: Sex = Sex.NOT_SPECIFIED
    specie_id: Optional[int] = Field(default=None, foreign_key="species.id")


class Pet(PetBase, table=True):
    """
    Extended pet model including breed, birth date, profile image, and audit timestamps.

    Enforces immutability of the `created_at` field at the model level.
    """

    breed: Optional[str] = None
    birthDate: Optional[datetime] = None
    profileImageURL: Optional[str] = None

    owner_id: int = Field(foreign_key="app_user.id")
    owner: Optional["User"] = Relationship(back_populates="pets")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __setattr__(self, name, value) -> None:
        """
        Prevent update for `created_at` field.
        NOTE: Ultimate protection should be enforced in the DB.
        """
        if name == "created_at" and hasattr(self, "created_at"):
            raise AttributeError("created_at is immutable")
        super().__setattr__(name, value)
