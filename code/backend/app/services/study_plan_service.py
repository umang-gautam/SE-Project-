"""
Study Plan service.
"""
from app.repositories import study_plan_repo

async def create_study_plan(data: dict) -> dict:
    return await study_plan_repo.create(data)

async def get_study_plan(plan_id: str) -> dict | None:
    return await study_plan_repo.get_by_id(plan_id)

async def get_study_plans_by_student(student_id: str) -> list[dict]:
    return await study_plan_repo.get_by_student(student_id)

async def update_study_plan(plan_id: str, data: dict) -> dict | None:
    return await study_plan_repo.update(plan_id, data)

async def delete_study_plan(plan_id: str) -> bool:
    return await study_plan_repo.delete(plan_id)
