"""Pydantic schemas for the StudySession entity."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class StudySessionCreate(BaseModel):
    """Schema for creating a new study session."""

    plan_id: str
    topic_id: str
    date: date
    duration_minutes: int = Field(..., gt=0)


class StudySessionUpdate(BaseModel):
    """Schema for updating a study session's status."""

    status: Literal["pending", "done", "missed"]


class StudySessionResponse(BaseModel):
    """Schema for returning study session data."""

    id: str
    plan_id: str
    topic_id: str
    date: date
    duration_minutes: int
    status: str

    model_config = {"from_attributes": True}
