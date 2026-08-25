from app.repositories import study_plans_repository


async def list_plans() -> list[dict]:
    return await study_plans_repository.get_all_plans()


async def get_plan(plan_id: int) -> dict | None:
    return await study_plans_repository.get_plan_by_id(plan_id)


async def list_plans_for_student(student_id: int) -> list[dict]:
    return await study_plans_repository.get_plans_for_student(student_id)


async def register_plan(student_id: int, week_start_date, status: str) -> dict:
    return await study_plans_repository.create_plan(student_id, week_start_date.isoformat(), status)
