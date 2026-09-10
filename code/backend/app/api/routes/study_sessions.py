from fastapi import APIRouter, HTTPException, status
from app.services import study_session_service
from app.schemas.study_session import StudySessionCreate, StudySessionUpdate, StudySessionResponse

router = APIRouter()

@router.post("/", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
async def create_study_session(session_in: StudySessionCreate):
    return await study_session_service.create_study_session(session_in.model_dump(exclude_unset=True))

@router.get("/{session_id}", response_model=StudySessionResponse)
async def get_study_session(session_id: str):
    session = await study_session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Study Session not found")
    return session

@router.get("/by-plan/{plan_id}", response_model=list[StudySessionResponse])
async def list_study_sessions_by_plan(plan_id: str):
    return await study_session_service.get_sessions_by_plan(plan_id)

@router.patch("/{session_id}", response_model=StudySessionResponse)
async def update_study_session(session_id: str, session_in: StudySessionUpdate):
    updated = await study_session_service.update_study_session(session_id, session_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Study Session not found")
    return updated

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_session(session_id: str):
    success = await study_session_service.delete_study_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Study Session not found")
