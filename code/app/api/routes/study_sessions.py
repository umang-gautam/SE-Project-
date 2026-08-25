from fastapi import APIRouter, HTTPException

from app.schemas.study_session import StudySessionCreate, StudySessionOut
from app.services import study_session_service

router = APIRouter(prefix="/study-sessions", tags=["Study Sessions"])


@router.get("/", response_model=list[StudySessionOut])
async def list_sessions():
    return await study_session_service.list_sessions()


@router.get("/{session_id}", response_model=StudySessionOut)
async def get_session(session_id: int):
    session = await study_session_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Study session not found")
    return session


@router.get("/plan/{plan_id}", response_model=list[StudySessionOut])
async def get_plan_sessions(plan_id: int):
    return await study_session_service.list_sessions_for_plan(plan_id)


@router.post("/", response_model=StudySessionOut, status_code=201)
async def create_session(payload: StudySessionCreate):
    return await study_session_service.register_session(
        payload.study_plan_id, payload.topic_id, payload.scheduled_start,
        payload.duration_minutes, payload.status, payload.rebalanced_from_session_id
    )
