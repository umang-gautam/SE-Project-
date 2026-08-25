from datetime import date
from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    subject_id: int
    title: str
    due_date: date
    weight: float = 1.0
    status: str = "pending"


class AssignmentOut(BaseModel):
    id: int
    subject_id: int
    title: str
    due_date: date
    weight: float
    status: str
