"""Pydantic schemas for the Assignment entity."""

from datetime import date

from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    """Schema for creating a new assignment."""

    topic_id: str
    due_date: date
    title: str


class AssignmentUpdate(BaseModel):
    """Schema for updating an existing assignment."""

    due_date: date | None = None
    title: str | None = None


class AssignmentResponse(BaseModel):
    """Schema for returning assignment data."""

    id: str
    topic_id: str
    due_date: date
    title: str

    model_config = {"from_attributes": True}
