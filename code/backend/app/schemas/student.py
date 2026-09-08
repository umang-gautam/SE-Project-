"""Pydantic schemas for the Student entity."""

from pydantic import BaseModel, Field, field_validator


class StudentCreate(BaseModel):
    """Schema for creating a new student."""

    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Ensure email contains an '@' symbol."""
        if "@" not in v:
            raise ValueError("email must contain '@'")
        return v


class StudentUpdate(BaseModel):
    """Schema for updating an existing student."""

    name: str | None = None
    email: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        """Ensure email contains an '@' symbol if provided."""
        if v is not None and "@" not in v:
            raise ValueError("email must contain '@'")
        return v


class StudentResponse(BaseModel):
    """Schema for returning student data."""

    id: str
    name: str
    email: str

    model_config = {"from_attributes": True}
