"""Pydantic schemas for the StudyPlan entity."""

from datetime import date

from pydantic import BaseModel, Field


class StudyPlanCreate(BaseModel):
    """Schema for creating a new study plan."""

    student_id: str
    start_date: date
    end_date: date


class StudyPlanUpdate(BaseModel):
    """Schema for updating an existing study plan."""

    start_date: date | None = None
    end_date: date | None = None


class StudyPlanResponse(BaseModel):
    """Schema for returning study plan data."""

    id: str
    student_id: str
    start_date: date
    end_date: date

    model_config = {"from_attributes": True}
