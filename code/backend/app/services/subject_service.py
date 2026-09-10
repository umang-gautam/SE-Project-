"""
Subject service.
"""
from app.repositories import subject_repo

async def create_subject(data: dict) -> dict:
    return await subject_repo.create(data)

async def get_subjects() -> list[dict]:
    return await subject_repo.get_all()

async def get_subject(subject_id: str) -> dict | None:
    return await subject_repo.get_by_id(subject_id)

async def update_subject(subject_id: str, data: dict) -> dict | None:
    return await subject_repo.update(subject_id, data)

async def delete_subject(subject_id: str) -> bool:
    return await subject_repo.delete(subject_id)
