from app.repositories import topics_repository


async def list_topics() -> list[dict]:
    return await topics_repository.get_all_topics()


async def get_topic(topic_id: int) -> dict | None:
    return await topics_repository.get_topic_by_id(topic_id)


async def list_topics_for_subject(subject_id: int) -> list[dict]:
    return await topics_repository.get_topics_for_subject(subject_id)


async def register_topic(subject_id: int, name: str, difficulty: int, estimated_hours: float) -> dict:
    return await topics_repository.create_topic(subject_id, name, difficulty, estimated_hours)
