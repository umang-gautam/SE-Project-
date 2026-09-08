"""Pydantic schemas for PerformanceRecord (append-only, no Update)."""

from datetime import datetime

from pydantic import BaseModel, Field


class PerformanceRecordCreate(BaseModel):
    """Schema for recording a student's score on a topic."""

    student_id: str
    topic_id: str
    score: float = Field(..., ge=0, le=100)


class PerformanceRecordResponse(BaseModel):
    """Schema for returning performance record data."""

    id: str
    student_id: str
    topic_id: str
    score: float
    recorded_at: datetime

    model_config = {"from_attributes": True}
