from datetime import datetime
from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    """What the client sends in the request body for POST /students"""
    name: str
    email: EmailStr


class StudentOut(BaseModel):
    """What we send back to the client — shape of a student row from Supabase"""
    id: int
    name: str
    email: str
    created_at: datetime