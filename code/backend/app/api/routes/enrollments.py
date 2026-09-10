from fastapi import APIRouter, HTTPException, status
from app.services import enrollment_service
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse

router = APIRouter()

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(enrollment_in: EnrollmentCreate):
    return await enrollment_service.create_enrollment(enrollment_in.model_dump(exclude_unset=True))

@router.get("/", response_model=list[EnrollmentResponse])
async def list_enrollments():
    return await enrollment_service.get_enrollments()

@router.get("/by-student/{student_id}", response_model=list[EnrollmentResponse])
async def list_enrollments_by_student(student_id: str):
    return await enrollment_service.get_enrollments_by_student(student_id)

@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(enrollment_id: str):
    success = await enrollment_service.delete_enrollment(enrollment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment not found")
