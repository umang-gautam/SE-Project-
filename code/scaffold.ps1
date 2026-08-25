# Run this from inside your project root (the folder that contains "app").
# It creates all directories and files for: subjects, enrollments, topics,
# assignments, performance_records, study_plans, study_sessions + main.py

$ErrorActionPreference = "Stop"

$dirs = @(
    "app\schemas",
    "app\repositories",
    "app\services",
    "app\api\routes"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

function Write-File($Path, $Content) {
    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Host "Wrote $Path"
}

# ---------------------------------------------------------------------------
# 1. Subjects
# ---------------------------------------------------------------------------

Write-File "app\schemas\subject.py" @'
from pydantic import BaseModel


class SubjectCreate(BaseModel):
    code: str
    name: str
    credits: float
    weekly_effort_hours: float


class SubjectOut(BaseModel):
    id: int
    code: str
    name: str
    credits: float
    weekly_effort_hours: float
'@

Write-File "app\repositories\subjects_repository.py" @'
from app.core.supabase_client import get_client


async def get_all_subjects() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/subjects")
        response.raise_for_status()
        return response.json()


async def get_subject_by_id(subject_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/subjects", params={"id": f"eq.{subject_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def create_subject(code: str, name: str, credits: float, weekly_effort_hours: float) -> dict:
    async with get_client() as client:
        response = await client.post("/subjects", json={
            "code": code, "name": name, "credits": credits, "weekly_effort_hours": weekly_effort_hours
        })
        response.raise_for_status()
        return response.json()[0]
'@

Write-File "app\services\subject_service.py" @'
from app.repositories import subjects_repository


async def list_subjects() -> list[dict]:
    return await subjects_repository.get_all_subjects()


async def get_subject(subject_id: int) -> dict | None:
    return await subjects_repository.get_subject_by_id(subject_id)


async def register_subject(code: str, name: str, credits: float, weekly_effort_hours: float) -> dict:
    return await subjects_repository.create_subject(code, name, credits, weekly_effort_hours)
'@

Write-File "app\api\routes\subjects.py" @'
from fastapi import APIRouter, HTTPException

from app.schemas.subject import SubjectCreate, SubjectOut
from app.services import subject_service

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("/", response_model=list[SubjectOut])
async def list_subjects():
    return await subject_service.list_subjects()


@router.get("/{subject_id}", response_model=SubjectOut)
async def get_subject(subject_id: int):
    subject = await subject_service.get_subject(subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.post("/", response_model=SubjectOut, status_code=201)
async def create_subject(payload: SubjectCreate):
    return await subject_service.register_subject(
        payload.code, payload.name, payload.credits, payload.weekly_effort_hours
    )
'@

# ---------------------------------------------------------------------------
# 2. Enrollments
# ---------------------------------------------------------------------------

Write-File "app\schemas\enrollment.py" @'
from datetime import datetime
from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    student_id: int
    subject_id: int
    target_grade: str | None = None


class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    subject_id: int
    enrolled_at: datetime
    target_grade: str | None = None
'@

Write-File "app\repositories\enrollments_repository.py" @'
from app.core.supabase_client import get_client


async def get_all_enrollments() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/enrollments")
        response.raise_for_status()
        return response.json()


async def get_enrollment_by_id(enrollment_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/enrollments", params={"id": f"eq.{enrollment_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_enrollments_for_student(student_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/enrollments", params={"student_id": f"eq.{student_id}"})
        response.raise_for_status()
        return response.json()


async def create_enrollment(student_id: int, subject_id: int, target_grade: str | None) -> dict:
    async with get_client() as client:
        response = await client.post("/enrollments", json={
            "student_id": student_id, "subject_id": subject_id, "target_grade": target_grade
        })
        response.raise_for_status()
        return response.json()[0]
'@

Write-File "app\services\enrollment_service.py" @'
from app.repositories import enrollments_repository


async def list_enrollments() -> list[dict]:
    return await enrollments_repository.get_all_enrollments()


async def get_enrollment(enrollment_id: int) -> dict | None:
    return await enrollments_repository.get_enrollment_by_id(enrollment_id)


async def list_enrollments_for_student(student_id: int) -> list[dict]:
    return await enrollments_repository.get_enrollments_for_student(student_id)


async def register_enrollment(student_id: int, subject_id: int, target_grade: str | None) -> dict:
    return await enrollments_repository.create_enrollment(student_id, subject_id, target_grade)
'@

Write-File "app\api\routes\enrollments.py" @'
from fastapi import APIRouter, HTTPException

from app.schemas.enrollment import EnrollmentCreate, EnrollmentOut
from app.services import enrollment_service

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.get("/", response_model=list[EnrollmentOut])
async def list_enrollments():
    return await enrollment_service.list_enrollments()


@router.get("/{enrollment_id}", response_model=EnrollmentOut)
async def get_enrollment(enrollment_id: int):
    enrollment = await enrollment_service.get_enrollment(enrollment_id)
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.get("/student/{student_id}", response_model=list[EnrollmentOut])
async def get_student_enrollments(student_id: int):
    return await enrollment_service.list_enrollments_for_student(student_id)


@router.post("/", response_model=EnrollmentOut, status_code=201)
async def create_enrollment(payload: EnrollmentCreate):
    return await enrollment_service.register_enrollment(
        payload.student_id, payload.subject_id, payload.target_grade
    )
'@

# ---------------------------------------------------------------------------
# 3. Topics
# ---------------------------------------------------------------------------

Write-File "app\schemas\topic.py" @'
from pydantic import BaseModel


class TopicCreate(BaseModel):
    subject_id: int
    name: str
    difficulty: int = 2
    estimated_hours: float = 2


class TopicOut(BaseModel):
    id: int
    subject_id: int
    name: str
    difficulty: int
    estimated_hours: float
'@

Write-File "app\repositories\topics_repository.py" @'
from app.core.supabase_client import get_client


async def get_all_topics() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/topics")
        response.raise_for_status()
        return response.json()


async def get_topic_by_id(topic_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/topics", params={"id": f"eq.{topic_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_topics_for_subject(subject_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/topics", params={"subject_id": f"eq.{subject_id}"})
        response.raise_for_status()
        return response.json()


async def create_topic(subject_id: int, name: str, difficulty: int, estimated_hours: float) -> dict:
    async with get_client() as client:
        response = await client.post("/topics", json={
            "subject_id": subject_id, "name": name,
            "difficulty": difficulty, "estimated_hours": estimated_hours
        })
        response.raise_for_status()
        return response.json()[0]
'@

Write-File "app\services\topic_service.py" @'
from app.repositories import topics_repository


async def list_topics() -> list[dict]:
    return await topics_repository.get_all_topics()


async def get_topic(topic_id: int) -> dict | None:
    return await topics_repository.get_topic_by_id(topic_id)


async def list_topics_for_subject(subject_id: int) -> list[dict]:
    return await topics_repository.get_topics_for_subject(subject_id)


async def register_topic(subject_id: int, name: str, difficulty: int, estimated_hours: float) -> dict:
    return await topics_repository.create_topic(subject_id, name, difficulty, estimated_hours)
'@

Write-File "app\api\routes\topics.py" @'
from fastapi import APIRouter, HTTPException

from app.schemas.topic import TopicCreate, TopicOut
from app.services import topic_service

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("/", response_model=list[TopicOut])
async def list_topics():
    return await topic_service.list_topics()


@router.get("/{topic_id}", response_model=TopicOut)
async def get_topic(topic_id: int):
    topic = await topic_service.get_topic(topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.get("/subject/{subject_id}", response_model=list[TopicOut])
async def get_subject_topics(subject_id: int):
    return await topic_service.list_topics_for_subject(subject_id)


@router.post("/", response_model=TopicOut, status_code=201)
async def create_topic(payload: TopicCreate):
    return await topic_service.register_topic(
        payload.subject_id, payload.name, payload.difficulty, payload.estimated_hours
    )
'@

# ---------------------------------------------------------------------------
# 4. Assignments
# ---------------------------------------------------------------------------

Write-File "app\schemas\assignment.py" @'
from datetime import date
from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    subject_id: int
    title: str
    due_date: date
    weight: float = 1.0
    status: str = "pending"


class AssignmentOut(BaseModel):
    id: int
    subject_id: int
    title: str
    due_date: date
    weight: float
    status: str
'@

Write-File "app\repositories\assignments_repository.py" @'
from app.core.supabase_client import get_client


async def get_all_assignments() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/assignments")
        response.raise_for_status()
        return response.json()


async def get_assignment_by_id(assignment_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/assignments", params={"id": f"eq.{assignment_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_assignments_for_subject(subject_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/assignments", params={"subject_id": f"eq.{subject_id}"})
        response.raise_for_status()
        return response.json()


async def create_assignment(subject_id: int, title: str, due_date: str, weight: float, status: str) -> dict:
    async with get_client() as client:
        response = await client.post("/assignments", json={
            "subject_id": subject_id, "title": title, "due_date": due_date,
            "weight": weight, "status": status
        })
        response.raise_for_status()
        return response.json()[0]
'@

Write-File "app\services\assignment_service.py" @'
from app.repositories import assignments_repository


async def list_assignments() -> list[dict]:
    return await assignments_repository.get_all_assignments()


async def get_assignment(assignment_id: int) -> dict | None:
    return await assignments_repository.get_assignment_by_id(assignment_id)


async def list_assignments_for_subject(subject_id: int) -> list[dict]:
    return await assignments_repository.get_assignments_for_subject(subject_id)


async def register_assignment(subject_id: int, title: str, due_date, weight: float, status: str) -> dict:
    return await assignments_repository.create_assignment(
        subject_id, title, due_date.isoformat(), weight, status
    )
'@

Write-File "app\api\routes\assignments.py" @'
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
'@

# ---------------------------------------------------------------------------
# 5. Performance Records
# ---------------------------------------------------------------------------

Write-File "app\schemas\performance_record.py" @'
from datetime import datetime
from pydantic import BaseModel


class PerformanceRecordCreate(BaseModel):
    student_id: int
    topic_id: int
    score: float
    record_type: str = "self_assessed"


class PerformanceRecordOut(BaseModel):
    id: int
    student_id: int
    topic_id: int
    score: float
    record_type: str
    recorded_at: datetime
'@

Write-File "app\repositories\performance_records_repository.py" @'
from app.core.supabase_client import get_client


async def get_all_records() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/performance_records")
        response.raise_for_status()
        return response.json()


async def get_record_by_id(record_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/performance_records", params={"id": f"eq.{record_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_records_for_student(student_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/performance_records", params={"student_id": f"eq.{student_id}"})
        response.raise_for_status()
        return response.json()


async def create_record(student_id: int, topic_id: int, score: float, record_type: str) -> dict:
    async with get_client() as client:
        response = await client.post("/performance_records", json={
            "student_id": student_id, "topic_id": topic_id,
            "score": score, "record_type": record_type
        })
        response.raise_for_status()
        return response.json()[0]
'@

Write-File "app\services\performance_record_service.py" @'
from app.repositories import performance_records_repository


async def list_records() -> list[dict]:
    return await performance_records_repository.get_all_records()


async def get_record(record_id: int) -> dict | None:
    return await performance_records_repository.get_record_by_id(record_id)


async def list_records_for_student(student_id: int) -> list[dict]:
    return await performance_records_repository.get_records_for_student(student_id)


async def register_record(student_id: int, topic_id: int, score: float, record_type: str) -> dict:
    return await performance_records_repository.create_record(student_id, topic_id, score, record_type)
'@

Write-File "app\api\routes\performance_records.py" @'
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
'@

# ---------------------------------------------------------------------------
# 6. Study Plans
# ---------------------------------------------------------------------------

Write-File "app\schemas\study_plan.py" @'
from datetime import date, datetime
from pydantic import BaseModel


class StudyPlanCreate(BaseModel):
    student_id: int
    week_start_date: date
    status: str = "active"


class StudyPlanOut(BaseModel):
    id: int
    student_id: int
    week_start_date: date
    status: str
    created_at: datetime
'@

Write-File "app\repositories\study_plans_repository.py" @'
from app.core.supabase_client import get_client


async def get_all_plans() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/study_plans")
        response.raise_for_status()
        return response.json()


async def get_plan_by_id(plan_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/study_plans", params={"id": f"eq.{plan_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_plans_for_student(student_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/study_plans", params={"student_id": f"eq.{student_id}"})
        response.raise_for_status()
        return response.json()


async def create_plan(student_id: int, week_start_date: str, status: str) -> dict:
    async with get_client() as client:
        response = await client.post("/study_plans", json={
            "student_id": student_id, "week_start_date": week_start_date, "status": status
        })
        response.raise_for_status()
        return response.json()[0]
'@

Write-File "app\services\study_plan_service.py" @'
from app.repositories import study_plans_repository


async def list_plans() -> list[dict]:
    return await study_plans_repository.get_all_plans()


async def get_plan(plan_id: int) -> dict | None:
    return await study_plans_repository.get_plan_by_id(plan_id)


async def list_plans_for_student(student_id: int) -> list[dict]:
    return await study_plans_repository.get_plans_for_student(student_id)


async def register_plan(student_id: int, week_start_date, status: str) -> dict:
    return await study_plans_repository.create_plan(student_id, week_start_date.isoformat(), status)
'@

Write-File "app\api\routes\study_plans.py" @'
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
'@

# ---------------------------------------------------------------------------
# 7. Study Sessions
# ---------------------------------------------------------------------------

Write-File "app\schemas\study_session.py" @'
from datetime import datetime
from pydantic import BaseModel


class StudySessionCreate(BaseModel):
    study_plan_id: int
    topic_id: int
    scheduled_start: datetime
    duration_minutes: int
    status: str = "pending"
    rebalanced_from_session_id: int | None = None


class StudySessionOut(BaseModel):
    id: int
    study_plan_id: int
    topic_id: int
    scheduled_start: datetime
    duration_minutes: int
    status: str
    rebalanced_from_session_id: int | None = None
'@

Write-File "app\repositories\study_sessions_repository.py" @'
from app.core.supabase_client import get_client


async def get_all_sessions() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/study_sessions")
        response.raise_for_status()
        return response.json()


async def get_session_by_id(session_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/study_sessions", params={"id": f"eq.{session_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_sessions_for_plan(plan_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/study_sessions", params={"study_plan_id": f"eq.{plan_id}"})
        response.raise_for_status()
        return response.json()


async def create_session(study_plan_id: int, topic_id: int, scheduled_start: str,
                          duration_minutes: int, status: str, rebalanced_from_session_id: int | None) -> dict:
    async with get_client() as client:
        response = await client.post("/study_sessions", json={
            "study_plan_id": study_plan_id, "topic_id": topic_id,
            "scheduled_start": scheduled_start, "duration_minutes": duration_minutes,
            "status": status, "rebalanced_from_session_id": rebalanced_from_session_id
        })
        response.raise_for_status()
        return response.json()[0]
'@

Write-File "app\services\study_session_service.py" @'
from app.repositories import study_sessions_repository


async def list_sessions() -> list[dict]:
    return await study_sessions_repository.get_all_sessions()


async def get_session(session_id: int) -> dict | None:
    return await study_sessions_repository.get_session_by_id(session_id)


async def list_sessions_for_plan(plan_id: int) -> list[dict]:
    return await study_sessions_repository.get_sessions_for_plan(plan_id)


async def register_session(study_plan_id: int, topic_id: int, scheduled_start,
                            duration_minutes: int, status: str, rebalanced_from_session_id: int | None) -> dict:
    return await study_sessions_repository.create_session(
        study_plan_id, topic_id, scheduled_start.isoformat(), duration_minutes, status, rebalanced_from_session_id
    )
'@

Write-File "app\api\routes\study_sessions.py" @'
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
'@

# ---------------------------------------------------------------------------
# main.py
# ---------------------------------------------------------------------------

Write-File "app\main.py" @'
from fastapi import FastAPI
from app.api.routes import (
    health, students, subjects, enrollments, topics,
    assignments, performance_records, study_plans, study_sessions
)
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health.router)
app.include_router(students.router)
app.include_router(subjects.router)
app.include_router(enrollments.router)
app.include_router(topics.router)
app.include_router(assignments.router)
app.include_router(performance_records.router)
app.include_router(study_plans.router)
app.include_router(study_sessions.router)
'@

Write-Host ""
Write-Host "Done. All files created."
Write-Host "Run: uvicorn app.main:app --reload"
Write-Host "Then check: http://127.0.0.1:8000/docs"
