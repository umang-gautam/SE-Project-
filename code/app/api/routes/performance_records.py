from fastapi import APIRouter, HTTPException

from app.schemas.performance_record import PerformanceRecordCreate, PerformanceRecordOut
from app.services import performance_record_service

router = APIRouter(prefix="/performance-records", tags=["Performance Records"])


@router.get("/", response_model=list[PerformanceRecordOut])
async def list_records():
    return await performance_record_service.list_records()


@router.get("/{record_id}", response_model=PerformanceRecordOut)
async def get_record(record_id: int):
    record = await performance_record_service.get_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return record


@router.get("/student/{student_id}", response_model=list[PerformanceRecordOut])
async def get_student_records(student_id: int):
    return await performance_record_service.list_records_for_student(student_id)


@router.post("/", response_model=PerformanceRecordOut, status_code=201)
async def create_record(payload: PerformanceRecordCreate):
    return await performance_record_service.register_record(
        payload.student_id, payload.topic_id, payload.score, payload.record_type
    )
