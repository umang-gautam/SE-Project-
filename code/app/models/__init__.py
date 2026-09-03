"""SQLAlchemy 2.0 models for the eight workload-balancer tables.

Importing this package registers every table on Base.metadata, so
`Base.metadata.create_all(engine)` builds the whole schema.
"""
from app.core.database import Base
from app.models.assignment import Assignment
from app.models.enrollment import Enrollment
from app.models.performance_record import PerformanceRecord
from app.models.student import Student
from app.models.study_plan import StudyPlan
from app.models.study_session import StudySession
from app.models.subject import Subject
from app.models.topic import Topic

__all__ = [
    "Base", "Student", "Subject", "Enrollment", "Topic",
    "Assignment", "PerformanceRecord", "StudyPlan", "StudySession",
]
