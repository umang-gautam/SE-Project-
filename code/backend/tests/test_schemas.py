"""
Unit tests for Pydantic schemas.

These are pure validation tests — no database, no mocking.
They prove that our schemas accept valid data and reject invalid data,
which is the whole point of having schemas.
"""

import pytest
from datetime import date, datetime
from pydantic import ValidationError

from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.schemas.subject import SubjectCreate, SubjectResponse
from app.schemas.performance import PerformanceRecordCreate, PerformanceRecordResponse
from app.schemas.study_session import StudySessionCreate, StudySessionUpdate


# ── Student schemas ───────────────────────────────────────────

class TestStudentCreate:
    def test_valid(self):
        s = StudentCreate(name="Alice", email="alice@example.com")
        assert s.name == "Alice"
        assert s.email == "alice@example.com"

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            StudentCreate(email="alice@example.com")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            StudentCreate(name="Alice")

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            StudentCreate(name="", email="alice@example.com")


class TestStudentUpdate:
    def test_partial_update_name_only(self):
        u = StudentUpdate(name="Bob")
        dumped = u.model_dump(exclude_unset=True)
        assert dumped == {"name": "Bob"}
        # email should NOT be in the dict since it wasn't set
        assert "email" not in dumped

    def test_empty_update_is_valid(self):
        """No fields set = valid (nothing to update)."""
        u = StudentUpdate()
        assert u.model_dump(exclude_unset=True) == {}


class TestStudentResponse:
    def test_from_dict(self):
        r = StudentResponse(id="abc-123", name="Alice", email="a@b.com")
        assert r.id == "abc-123"


# ── Subject schemas ───────────────────────────────────────────

class TestSubjectCreate:
    def test_valid(self):
        s = SubjectCreate(name="Data Structures", code="CS201")
        assert s.code == "CS201"

    def test_empty_code_rejected(self):
        with pytest.raises(ValidationError):
            SubjectCreate(name="DS", code="")


# ── Performance schemas ───────────────────────────────────────

class TestPerformanceRecordCreate:
    def test_valid_score(self):
        p = PerformanceRecordCreate(
            student_id="s1", topic_id="t1", score=85.5
        )
        assert p.score == 85.5

    def test_score_below_zero_rejected(self):
        with pytest.raises(ValidationError):
            PerformanceRecordCreate(
                student_id="s1", topic_id="t1", score=-1
            )

    def test_score_above_100_rejected(self):
        with pytest.raises(ValidationError):
            PerformanceRecordCreate(
                student_id="s1", topic_id="t1", score=101
            )

    def test_score_boundary_zero(self):
        p = PerformanceRecordCreate(
            student_id="s1", topic_id="t1", score=0
        )
        assert p.score == 0

    def test_score_boundary_100(self):
        p = PerformanceRecordCreate(
            student_id="s1", topic_id="t1", score=100
        )
        assert p.score == 100


# ── Study session schemas ─────────────────────────────────────

class TestStudySessionCreate:
    def test_valid(self):
        s = StudySessionCreate(
            plan_id="p1", topic_id="t1",
            date=date(2025, 1, 15), duration_minutes=60,
        )
        assert s.duration_minutes == 60

    def test_zero_duration_rejected(self):
        with pytest.raises(ValidationError):
            StudySessionCreate(
                plan_id="p1", topic_id="t1",
                date=date(2025, 1, 15), duration_minutes=0,
            )

    def test_negative_duration_rejected(self):
        with pytest.raises(ValidationError):
            StudySessionCreate(
                plan_id="p1", topic_id="t1",
                date=date(2025, 1, 15), duration_minutes=-30,
            )


class TestStudySessionUpdate:
    def test_valid_statuses(self):
        for status in ("pending", "done", "missed"):
            u = StudySessionUpdate(status=status)
            assert u.status == status

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            StudySessionUpdate(status="cancelled")
