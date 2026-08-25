from datetime import date, datetime
from pydantic import BaseModel


class StudyPlanCreate(BaseModel):
    student_id: int
    week_start_date: date
    status: str = "active"


class StudyPlanOut(BaseModel):
    id: int
    student_id: int
    week_start_date: date
    status: str
    created_at: datetime
