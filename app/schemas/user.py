# app/schemas/user.py


from pydantic import BaseModel, EmailStr, Field, field_validator

# from app.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    def password_strength(cls, v):
        """Check user password complexity."""
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number.")
        return v


# class UserDetailsResponse(BaseModel):
#     email: EmailStr
#     name: Optional[str] = None
#     is_verified: bool
#     role: Role

#     @computed_field
#     @property
#     def initial(self) -> str:
#         return self.name[0].upper() if self.name else self.email[0].upper()
