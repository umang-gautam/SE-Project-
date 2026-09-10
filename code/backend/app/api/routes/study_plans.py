from fastapi import APIRouter, HTTPException, status
from app.services import study_plan_service, plan_service
from app.schemas.study_plan import StudyPlanCreate, StudyPlanResponse
from app.schemas.scoring import PlanGenerateRequest, PlanGenerateResponse

router = APIRouter()

@router.post("/", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_study_plan(plan_in: StudyPlanCreate):
    return await study_plan_service.create_study_plan(plan_in.model_dump(exclude_unset=True))

@router.get("/{plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(plan_id: str):
    plan = await study_plan_service.get_study_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Study Plan not found")
    return plan

@router.get("/by-student/{student_id}", response_model=list[StudyPlanResponse])
async def list_study_plans_by_student(student_id: str):
    return await study_plan_service.get_study_plans_by_student(student_id)

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_plan(plan_id: str):
    success = await study_plan_service.delete_study_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Study Plan not found")


@router.post("/generate", response_model=PlanGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_study_plan(req: PlanGenerateRequest):
    """Score all enrolled topics and generate a time-allocated study plan."""
    result = await plan_service.generate_plan(
        student_id=req.student_id,
        hours_per_day=req.hours_per_day,
        num_days=req.num_days,
        start_date=req.start_date,
    )
    return result
