"""Pydantic schemas for the Enrollment entity (no Update — enroll or unenroll)."""

from pydantic import BaseModel, Field


class EnrollmentCreate(BaseModel):
    """Schema for enrolling a student into a subject."""

    student_id: str
    subject_id: str


class EnrollmentResponse(BaseModel):
    """Schema for returning enrollment data."""

    id: str
    student_id: str
    subject_id: str

    model_config = {"from_attributes": True}
