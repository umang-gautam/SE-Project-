from fastapi import APIRouter, HTTPException

from app.schemas.study_plan import StudyPlanCreate, StudyPlanOut
from app.services import study_plan_service

router = APIRouter(prefix="/study-plans", tags=["Study Plans"])


@router.get("/", response_model=list[StudyPlanOut])
async def list_plans():
    return await study_plan_service.list_plans()


@router.get("/{plan_id}", response_model=StudyPlanOut)
async def get_plan(plan_id: int):
    plan = await study_plan_service.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan


@router.get("/student/{student_id}", response_model=list[StudyPlanOut])
async def get_student_plans(student_id: int):
    return await study_plan_service.list_plans_for_student(student_id)


@router.post("/", response_model=StudyPlanOut, status_code=201)
async def create_plan(payload: StudyPlanCreate):
    return await study_plan_service.register_plan(
        payload.student_id, payload.week_start_date, payload.status
    )
