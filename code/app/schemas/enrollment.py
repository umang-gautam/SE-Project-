from datetime import datetime
from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    student_id: int
    subject_id: int
    target_grade: str | None = None


class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    subject_id: int
    enrolled_at: datetime
    target_grade: str | None = None
