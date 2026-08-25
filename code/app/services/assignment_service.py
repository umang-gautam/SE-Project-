from app.repositories import assignments_repository


async def list_assignments() -> list[dict]:
    return await assignments_repository.get_all_assignments()


async def get_assignment(assignment_id: int) -> dict | None:
    return await assignments_repository.get_assignment_by_id(assignment_id)


async def list_assignments_for_subject(subject_id: int) -> list[dict]:
    return await assignments_repository.get_assignments_for_subject(subject_id)


async def register_assignment(subject_id: int, title: str, due_date, weight: float, status: str) -> dict:
    return await assignments_repository.create_assignment(
        subject_id, title, due_date.isoformat(), weight, status
    )
