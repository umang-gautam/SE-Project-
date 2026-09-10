from fastapi import APIRouter, HTTPException, status
from app.services import performance_service
from app.schemas.performance import PerformanceRecordCreate, PerformanceRecordResponse

router = APIRouter()

@router.post("/", response_model=PerformanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_record(record_in: PerformanceRecordCreate):
    return await performance_service.create_performance_record(record_in.model_dump(exclude_unset=True))

@router.get("/by-student/{student_id}", response_model=list[PerformanceRecordResponse])
async def list_records_by_student(student_id: str):
    return await performance_service.get_records_by_student(student_id)

@router.get("/by-student/{student_id}/topic/{topic_id}", response_model=list[PerformanceRecordResponse])
async def list_records_by_student_and_topic(student_id: str, topic_id: str):
    return await performance_service.get_records_by_student_and_topic(student_id, topic_id)
