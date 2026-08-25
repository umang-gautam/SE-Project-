from app.repositories import performance_records_repository


async def list_records() -> list[dict]:
    return await performance_records_repository.get_all_records()


async def get_record(record_id: int) -> dict | None:
    return await performance_records_repository.get_record_by_id(record_id)


async def list_records_for_student(student_id: int) -> list[dict]:
    return await performance_records_repository.get_records_for_student(student_id)


async def register_record(student_id: int, topic_id: int, score: float, record_type: str) -> dict:
    return await performance_records_repository.create_record(student_id, topic_id, score, record_type)
