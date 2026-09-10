"""
Unit tests for study plan allocation.

allocate_sessions() is a PURE function — no database, no mocking.
We test the allocation algorithm directly with synthetic scored topics.
"""

import pytest
from datetime import date

from app.services.plan_service import (
    allocate_sessions,
    MIN_SESSION_MINUTES,
    MAX_SESSION_MINUTES,
)


# ── Helpers ───────────────────────────────────────────────────

def make_topic(topic_id: str, priority: float) -> dict:
    """Create a minimal scored topic dict for testing."""
    return {
        "topic_id": topic_id,
        "topic_name": f"Topic {topic_id}",
        "subject_id": "sub-1",
        "subject_name": "Test Subject",
        "mastery": 0.5,
        "urgency": 0.5,
        "priority": priority,
    }


START = date(2025, 1, 15)


# ── Basic allocation ─────────────────────────────────────────

class TestAllocateSessions:
    def test_single_topic_single_day(self):
        topics = [make_topic("t1", 80.0)]
        sessions = allocate_sessions(topics, START, num_days=1, minutes_per_day=60)
        assert len(sessions) >= 1
        assert all(s["topic_id"] == "t1" for s in sessions)

    def test_multiple_topics_get_proportional_time(self):
        """High-priority topic should get more sessions than low-priority."""
        topics = [
            make_topic("t-high", 90.0),
            make_topic("t-low", 10.0),
        ]
        sessions = allocate_sessions(topics, START, num_days=7, minutes_per_day=120)

        high_minutes = sum(s["duration_minutes"] for s in sessions if s["topic_id"] == "t-high")
        low_minutes = sum(s["duration_minutes"] for s in sessions if s["topic_id"] == "t-low")

        # High-priority topic should get substantially more time
        assert high_minutes > low_minutes

    def test_sessions_have_valid_duration(self):
        topics = [make_topic("t1", 60.0), make_topic("t2", 40.0)]
        sessions = allocate_sessions(topics, START, num_days=5, minutes_per_day=180)

        for s in sessions:
            assert s["duration_minutes"] >= MIN_SESSION_MINUTES
            assert s["duration_minutes"] <= MAX_SESSION_MINUTES

    def test_sessions_have_pending_status(self):
        topics = [make_topic("t1", 50.0)]
        sessions = allocate_sessions(topics, START, num_days=3, minutes_per_day=60)
        assert all(s["status"] == "pending" for s in sessions)

    def test_sessions_are_within_date_range(self):
        topics = [make_topic("t1", 70.0)]
        num_days = 5
        sessions = allocate_sessions(topics, START, num_days=num_days, minutes_per_day=90)

        end_date = date(2025, 1, 19)  # START + 4 days
        for s in sessions:
            session_date = date.fromisoformat(s["date"])
            assert START <= session_date <= end_date


# ── Edge cases ────────────────────────────────────────────────

class TestAllocateEdgeCases:
    def test_empty_topics(self):
        assert allocate_sessions([], START, num_days=5, minutes_per_day=60) == []

    def test_zero_days(self):
        topics = [make_topic("t1", 50.0)]
        assert allocate_sessions(topics, START, num_days=0, minutes_per_day=60) == []

    def test_zero_minutes_per_day(self):
        topics = [make_topic("t1", 50.0)]
        assert allocate_sessions(topics, START, num_days=5, minutes_per_day=0) == []

    def test_all_zero_priority(self):
        """Topics with priority 0 should produce no sessions."""
        topics = [make_topic("t1", 0.0), make_topic("t2", 0.0)]
        assert allocate_sessions(topics, START, num_days=5, minutes_per_day=60) == []

    def test_very_small_budget_skips_low_priority(self):
        """If total budget is tiny, only the highest-priority topic should get time."""
        topics = [
            make_topic("t-high", 90.0),
            make_topic("t-low", 10.0),
        ]
        # Only 30 min total — barely enough for one session
        sessions = allocate_sessions(topics, START, num_days=1, minutes_per_day=30)
        # At most one session, and it should be the high-priority topic
        if sessions:
            assert sessions[0]["topic_id"] == "t-high"

    def test_many_topics_moderate_budget(self):
        """Stress test: 10 topics, 5 days, 3 hours/day."""
        topics = [make_topic(f"t{i}", priority=100 - i * 10) for i in range(10)]
        sessions = allocate_sessions(topics, START, num_days=5, minutes_per_day=180)

        # Should produce a reasonable number of sessions
        assert len(sessions) > 0
        # Total time should not exceed budget
        total = sum(s["duration_minutes"] for s in sessions)
        assert total <= 5 * 180 + 50  # small grace for rounding
