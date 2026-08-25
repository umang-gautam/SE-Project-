from fastapi import APIRouter, HTTPException

from app.schemas.subject import SubjectCreate, SubjectOut
from app.services import subject_service

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("/", response_model=list[SubjectOut])
async def list_subjects():
    return await subject_service.list_subjects()


@router.get("/{subject_id}", response_model=SubjectOut)
async def get_subject(subject_id: int):
    subject = await subject_service.get_subject(subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.post("/", response_model=SubjectOut, status_code=201)
async def create_subject(payload: SubjectCreate):
    return await subject_service.register_subject(
        payload.code, payload.name, payload.credits, payload.weekly_effort_hours
    )
