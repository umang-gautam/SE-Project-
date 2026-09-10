"""
Assignment service.
"""
from app.repositories import assignment_repo

async def create_assignment(data: dict) -> dict:
    return await assignment_repo.create(data)

async def get_assignments() -> list[dict]:
    return await assignment_repo.get_all()

async def get_assignments_by_topic(topic_id: str) -> list[dict]:
    return await assignment_repo.get_by_topic(topic_id)

async def get_assignment(assignment_id: str) -> dict | None:
    return await assignment_repo.get_by_id(assignment_id)

async def update_assignment(assignment_id: str, data: dict) -> dict | None:
    return await assignment_repo.update(assignment_id, data)

async def delete_assignment(assignment_id: str) -> bool:
    return await assignment_repo.delete(assignment_id)
