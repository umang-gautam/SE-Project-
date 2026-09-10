"""
Student service.
"""
from app.repositories import student_repo

async def create_student(data: dict) -> dict:
    return await student_repo.create(data)

async def get_students() -> list[dict]:
    return await student_repo.get_all()

async def get_student(student_id: str) -> dict | None:
    return await student_repo.get_by_id(student_id)

async def update_student(student_id: str, data: dict) -> dict | None:
    return await student_repo.update(student_id, data)

async def delete_student(student_id: str) -> bool:
    return await student_repo.delete(student_id)
