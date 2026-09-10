from fastapi import APIRouter, HTTPException, status
from app.services import subject_service
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse

router = APIRouter()

@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(subject_in: SubjectCreate):
    return await subject_service.create_subject(subject_in.model_dump(exclude_unset=True))

@router.get("/", response_model=list[SubjectResponse])
async def list_subjects():
    return await subject_service.get_subjects()

@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: str):
    subject = await subject_service.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.patch("/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: str, subject_in: SubjectUpdate):
    updated = await subject_service.update_subject(subject_id, subject_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Subject not found")
    return updated

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(subject_id: str):
    success = await subject_service.delete_subject(subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
