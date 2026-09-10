from fastapi import APIRouter, HTTPException, status
from app.services import student_service, plan_service
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.schemas.scoring import TopicScoreResponse

router = APIRouter()

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(student_in: StudentCreate):
    created = await student_service.create_student(student_in.model_dump(exclude_unset=True))
    return created

@router.get("/", response_model=list[StudentResponse])
async def list_students():
    return await student_service.get_students()

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str):
    student = await student_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: str, student_in: StudentUpdate):
    updated = await student_service.update_student(student_id, student_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: str):
    success = await student_service.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")


@router.get("/{student_id}/scores", response_model=list[TopicScoreResponse])
async def get_student_scores(student_id: str):
    """Return all enrolled topics scored by priority (highest first)."""
    # Verify student exists
    student = await student_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await plan_service.get_student_topic_scores(student_id)
