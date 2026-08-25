from fastapi import APIRouter, HTTPException

from app.schemas.student import StudentCreate, StudentOut
from app.services import student_service

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=list[StudentOut])
async def list_students():
    return await student_service.list_students()


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(student_id: int):
    student = await student_service.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=StudentOut, status_code=201)
async def create_student(payload: StudentCreate):
    return await student_service.register_student(payload.name, payload.email)