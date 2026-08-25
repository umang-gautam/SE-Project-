from pydantic import BaseModel


class SubjectCreate(BaseModel):
    code: str
    name: str
    credits: float
    weekly_effort_hours: float


class SubjectOut(BaseModel):
    id: int
    code: str
    name: str
    credits: float
    weekly_effort_hours: float
