"""Pydantic schemas for the Topic entity."""

from pydantic import BaseModel, Field


class TopicCreate(BaseModel):
    """Schema for creating a new topic."""

    subject_id: str
    name: str


class TopicUpdate(BaseModel):
    """Schema for updating an existing topic."""

    name: str | None = None


class TopicResponse(BaseModel):
    """Schema for returning topic data."""

    id: str
    subject_id: str
    name: str

    model_config = {"from_attributes": True}
