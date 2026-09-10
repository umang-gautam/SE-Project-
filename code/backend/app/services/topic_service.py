"""
Topic service.
"""
from app.repositories import topic_repo

async def create_topic(data: dict) -> dict:
    return await topic_repo.create(data)

async def get_topics() -> list[dict]:
    return await topic_repo.get_all()

async def get_topics_by_subject(subject_id: str) -> list[dict]:
    return await topic_repo.get_by_subject(subject_id)

async def get_topic(topic_id: str) -> dict | None:
    return await topic_repo.get_by_id(topic_id)

async def update_topic(topic_id: str, data: dict) -> dict | None:
    return await topic_repo.update(topic_id, data)

async def delete_topic(topic_id: str) -> bool:
    return await topic_repo.delete(topic_id)
