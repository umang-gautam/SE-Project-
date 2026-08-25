from pydantic import BaseModel


class TopicCreate(BaseModel):
    subject_id: int
    name: str
    difficulty: int = 2
    estimated_hours: float = 2


class TopicOut(BaseModel):
    id: int
    subject_id: int
    name: str
    difficulty: int
    estimated_hours: float
