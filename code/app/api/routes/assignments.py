from fastapi import APIRouter, HTTPException

from app.schemas.assignment import AssignmentCreate, AssignmentOut
from app.services import assignment_service

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.get("/", response_model=list[AssignmentOut])
async def list_assignments():
    return await assignment_service.list_assignments()


@router.get("/{assignment_id}", response_model=AssignmentOut)
async def get_assignment(assignment_id: int):
    assignment = await assignment_service.get_assignment(assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.get("/subject/{subject_id}", response_model=list[AssignmentOut])
async def get_subject_assignments(subject_id: int):
    return await assignment_service.list_assignments_for_subject(subject_id)


@router.post("/", response_model=AssignmentOut, status_code=201)
async def create_assignment(payload: AssignmentCreate):
    return await assignment_service.register_assignment(
        payload.subject_id, payload.title, payload.due_date, payload.weight, payload.status
    )
