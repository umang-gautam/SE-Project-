from datetime import datetime
from pydantic import BaseModel


class PerformanceRecordCreate(BaseModel):
    student_id: int
    topic_id: int
    score: float
    record_type: str = "self_assessed"


class PerformanceRecordOut(BaseModel):
    id: int
    student_id: int
    topic_id: int
    score: float
    record_type: str
    recorded_at: datetime
