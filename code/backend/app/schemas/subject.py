"""Pydantic schemas for the Subject entity."""

from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    """Schema for creating a new subject."""

    name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)


class SubjectUpdate(BaseModel):
    """Schema for updating an existing subject."""

    name: str | None = None
    code: str | None = None


class SubjectResponse(BaseModel):
    """Schema for returning subject data."""

    id: str
    name: str
    code: str

    model_config = {"from_attributes": True}
