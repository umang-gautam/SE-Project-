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
