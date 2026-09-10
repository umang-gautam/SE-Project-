"""
Performance service.
"""
from app.repositories import performance_repo

async def create_performance_record(data: dict) -> dict:
    return await performance_repo.create(data)

async def get_records_by_student(student_id: str) -> list[dict]:
    return await performance_repo.get_by_student(student_id)

async def get_records_by_student_and_topic(student_id: str, topic_id: str) -> list[dict]:
    return await performance_repo.get_by_student_and_topic(student_id, topic_id)
