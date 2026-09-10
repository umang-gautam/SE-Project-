"""
Enrollment service.
"""
from app.repositories import enrollment_repo

async def create_enrollment(data: dict) -> dict:
    return await enrollment_repo.create(data)

async def get_enrollments() -> list[dict]:
    return await enrollment_repo.get_all()

async def get_enrollments_by_student(student_id: str) -> list[dict]:
    return await enrollment_repo.get_by_student(student_id)

async def get_enrollment(enrollment_id: str) -> dict | None:
    return await enrollment_repo.get_by_id(enrollment_id)

async def delete_enrollment(enrollment_id: str) -> bool:
    return await enrollment_repo.delete(enrollment_id)
