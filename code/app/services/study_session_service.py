from app.repositories import study_sessions_repository


async def list_sessions() -> list[dict]:
    return await study_sessions_repository.get_all_sessions()


async def get_session(session_id: int) -> dict | None:
    return await study_sessions_repository.get_session_by_id(session_id)


async def list_sessions_for_plan(plan_id: int) -> list[dict]:
    return await study_sessions_repository.get_sessions_for_plan(plan_id)


async def register_session(study_plan_id: int, topic_id: int, scheduled_start,
                            duration_minutes: int, status: str, rebalanced_from_session_id: int | None) -> dict:
    return await study_sessions_repository.create_session(
        study_plan_id, topic_id, scheduled_start.isoformat(), duration_minutes, status, rebalanced_from_session_id
    )
