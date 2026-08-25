from app.repositories import enrollments_repository


async def list_enrollments() -> list[dict]:
    return await enrollments_repository.get_all_enrollments()


async def get_enrollment(enrollment_id: int) -> dict | None:
    return await enrollments_repository.get_enrollment_by_id(enrollment_id)


async def list_enrollments_for_student(student_id: int) -> list[dict]:
    return await enrollments_repository.get_enrollments_for_student(student_id)


async def register_enrollment(student_id: int, subject_id: int, target_grade: str | None) -> dict:
    return await enrollments_repository.create_enrollment(student_id, subject_id, target_grade)
