"""
Study Session service.
"""
from app.repositories import study_session_repo

async def create_study_session(data: dict) -> dict:
    return await study_session_repo.create(data)

async def get_session(session_id: str) -> dict | None:
    return await study_session_repo.get_by_id(session_id)

async def get_sessions_by_plan(plan_id: str) -> list[dict]:
    return await study_session_repo.get_by_plan(plan_id)

async def update_study_session(session_id: str, data: dict) -> dict | None:
    return await study_session_repo.update(session_id, data)

async def delete_study_session(session_id: str) -> bool:
    return await study_session_repo.delete(session_id)
