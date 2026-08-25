from app.repositories import students_repository


async def list_students() -> list[dict]:
    return await students_repository.get_all_students()


async def get_student(student_id: int) -> dict | None:
    return await students_repository.get_student_by_id(student_id)


async def register_student(name: str, email: str) -> dict:
    # Business rules go here later, e.g.:
    # - check if email already exists before inserting
    # - normalize name casing
    # For now, this is a direct pass-through to the repository.
    return await students_repository.create_student(name, email)