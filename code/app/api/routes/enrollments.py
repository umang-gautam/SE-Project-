from fastapi import APIRouter, HTTPException

from app.schemas.enrollment import EnrollmentCreate, EnrollmentOut
from app.services import enrollment_service

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.get("/", response_model=list[EnrollmentOut])
async def list_enrollments():
    return await enrollment_service.list_enrollments()


@router.get("/{enrollment_id}", response_model=EnrollmentOut)
async def get_enrollment(enrollment_id: int):
    enrollment = await enrollment_service.get_enrollment(enrollment_id)
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.get("/student/{student_id}", response_model=list[EnrollmentOut])
async def get_student_enrollments(student_id: int):
    return await enrollment_service.list_enrollments_for_student(student_id)


@router.post("/", response_model=EnrollmentOut, status_code=201)
async def create_enrollment(payload: EnrollmentCreate):
    return await enrollment_service.register_enrollment(
        payload.student_id, payload.subject_id, payload.target_grade
    )
