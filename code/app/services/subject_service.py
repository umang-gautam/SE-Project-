from app.repositories import subjects_repository


async def list_subjects() -> list[dict]:
    return await subjects_repository.get_all_subjects()


async def get_subject(subject_id: int) -> dict | None:
    return await subjects_repository.get_subject_by_id(subject_id)


async def register_subject(code: str, name: str, credits: float, weekly_effort_hours: float) -> dict:
    return await subjects_repository.create_subject(code, name, credits, weekly_effort_hours)
