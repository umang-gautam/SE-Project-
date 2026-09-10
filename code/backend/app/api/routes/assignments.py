from fastapi import APIRouter, HTTPException, status
from app.services import assignment_service
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse

router = APIRouter()

@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(assignment_in: AssignmentCreate):
    return await assignment_service.create_assignment(assignment_in.model_dump(exclude_unset=True))

@router.get("/", response_model=list[AssignmentResponse])
async def list_assignments():
    return await assignment_service.get_assignments()

@router.get("/by-topic/{topic_id}", response_model=list[AssignmentResponse])
async def get_assignments_by_topic(topic_id: str):
    return await assignment_service.get_assignments_by_topic(topic_id)

@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: str):
    assignment = await assignment_service.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(assignment_id: str, assignment_in: AssignmentUpdate):
    updated = await assignment_service.update_assignment(assignment_id, assignment_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return updated

@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(assignment_id: str):
    success = await assignment_service.delete_assignment(assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
