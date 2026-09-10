"""Pydantic schemas for scoring and plan generation requests/responses."""

from datetime import date
from pydantic import BaseModel, Field


# ── Scoring ───────────────────────────────────────────────────

class TopicScoreResponse(BaseModel):
    """Scored topic returned by GET /students/{id}/scores."""
    topic_id: str
    topic_name: str
    subject_id: str
    subject_name: str
    mastery: float
    urgency: float
    priority: float


# ── Plan generation ───────────────────────────────────────────

class PlanGenerateRequest(BaseModel):
    """Input for POST /study-plans/generate."""
    student_id: str
    hours_per_day: float = Field(..., gt=0, le=12)
    num_days: int = Field(..., gt=0, le=90)
    start_date: date | None = None  # defaults to today

    model_config = {"json_schema_extra": {
        "examples": [{
            "student_id": "abc-123",
            "hours_per_day": 3,
            "num_days": 7,
        }]
    }}


class SessionOut(BaseModel):
    """A single study session within a generated plan."""
    id: str
    topic_id: str
    date: date
    duration_minutes: int
    status: str


class PlanGenerateResponse(BaseModel):
    """Output of POST /study-plans/generate."""
    plan_id: str
    student_id: str
    start_date: date
    end_date: date
    sessions: list[SessionOut]
    topic_scores: list[TopicScoreResponse]
