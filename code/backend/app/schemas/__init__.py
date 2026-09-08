"""
Pydantic schemas package for the Workload Balancer application.

Exports all request and response models for students, subjects,
enrollments, topics, assignments, performance records, study plans,
and study sessions.
"""

from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
)
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
)
from app.schemas.performance import (
    PerformanceRecordCreate,
    PerformanceRecordResponse,
)
from app.schemas.student import (
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)
from app.schemas.study_plan import (
    StudyPlanCreate,
    StudyPlanResponse,
    StudyPlanUpdate,
)
from app.schemas.study_session import (
    StudySessionCreate,
    StudySessionResponse,
    StudySessionUpdate,
)
from app.schemas.subject import (
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
)
from app.schemas.topic import (
    TopicCreate,
    TopicResponse,
    TopicUpdate,
)

__all__ = [
    # Student
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    # Subject
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectResponse",
    # Enrollment
    "EnrollmentCreate",
    "EnrollmentResponse",
    # Topic
    "TopicCreate",
    "TopicUpdate",
    "TopicResponse",
    # Assignment
    "AssignmentCreate",
    "AssignmentUpdate",
    "AssignmentResponse",
    # Performance
    "PerformanceRecordCreate",
    "PerformanceRecordResponse",
    # Study Plan
    "StudyPlanCreate",
    "StudyPlanUpdate",
    "StudyPlanResponse",
    # Study Session
    "StudySessionCreate",
    "StudySessionUpdate",
    "StudySessionResponse",
]
