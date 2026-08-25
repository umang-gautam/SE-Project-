from datetime import datetime
from pydantic import BaseModel


class StudySessionCreate(BaseModel):
    study_plan_id: int
    topic_id: int
    scheduled_start: datetime
    duration_minutes: int
    status: str = "pending"
    rebalanced_from_session_id: int | None = None


class StudySessionOut(BaseModel):
    id: int
    study_plan_id: int
    topic_id: int
    scheduled_start: datetime
    duration_minutes: int
    status: str
    rebalanced_from_session_id: int | None = None
