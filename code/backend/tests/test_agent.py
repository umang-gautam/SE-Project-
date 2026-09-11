"""
Tests for the LangGraph rebalancing agent.

We mock agent/tools.py so the graph runs without a database.
This tests the state machine flow: which nodes execute, what
state transitions happen, and what the final output looks like.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import date


# ── Mock data ─────────────────────────────────────────────────

MOCK_PLAN = {
    "id": "plan-001",
    "student_id": "stu-001",
    "start_date": "2025-01-15",
    "end_date": "2025-01-21",
    "sessions": [
        {"id": "sess-1", "topic_id": "t1", "duration_minutes": 45, "status": "pending"},
        {"id": "sess-2", "topic_id": "t2", "duration_minutes": 45, "status": "missed"},
    ],
}

MOCK_SCORES = [
    {"topic_id": "t1", "topic_name": "Linked Lists", "subject_id": "s1",
     "subject_name": "DSA", "mastery": 0.3, "urgency": 0.8, "priority": 74.0},
    {"topic_id": "t2", "topic_name": "Sorting", "subject_id": "s1",
     "subject_name": "DSA", "mastery": 0.7, "urgency": 0.5, "priority": 38.0},
]

MOCK_NEW_PLAN = {
    "plan_id": "plan-002",
    "student_id": "stu-001",
    "start_date": "2025-01-16",
    "end_date": "2025-01-21",
    "sessions": [
        {"id": "sess-3", "topic_id": "t1", "date": "2025-01-16", "duration_minutes": 45, "status": "pending"},
    ],
    "topic_scores": MOCK_SCORES,
}


# ── Test: Manual trigger → full rebalance ─────────────────────

class TestAgentManualTrigger:
    @pytest.mark.asyncio
    @patch("app.agent.graph.tools")
    async def test_manual_trigger_runs_full_flow(self, mock_tools):
        """Manual trigger → detect_change → re_score → re_plan → explain."""
        mock_tools.get_plan = AsyncMock(return_value=MOCK_PLAN)
        mock_tools.get_scores = AsyncMock(return_value=MOCK_SCORES)
        mock_tools.regenerate_plan = AsyncMock(return_value=MOCK_NEW_PLAN)

        from app.agent.graph import rebalance_graph

        result = await rebalance_graph.ainvoke({
            "student_id": "stu-001",
            "trigger": "manual",
            "trigger_details": {},
        })

        assert result["changes_needed"] is True
        assert result["explanation"]  # non-empty
        assert result["new_plan"] is not None
        mock_tools.get_scores.assert_called_once()
        mock_tools.regenerate_plan.assert_called_once()


# ── Test: Missed session → rebalance ──────────────────────────

class TestAgentMissedSession:
    @pytest.mark.asyncio
    @patch("app.agent.graph.tools")
    async def test_missed_session_triggers_rebalance(self, mock_tools):
        mock_tools.get_plan = AsyncMock(return_value=MOCK_PLAN)
        mock_tools.get_scores = AsyncMock(return_value=MOCK_SCORES)
        mock_tools.regenerate_plan = AsyncMock(return_value=MOCK_NEW_PLAN)

        from app.agent.graph import rebalance_graph

        result = await rebalance_graph.ainvoke({
            "student_id": "stu-001",
            "trigger": "missed_session",
            "trigger_details": {"session_id": "sess-2"},
        })

        assert result["changes_needed"] is True
        assert "missed" in result["explanation"].lower()


# ── Test: Good score → no rebalance ───────────────────────────

class TestAgentNoChangeNeeded:
    @pytest.mark.asyncio
    @patch("app.agent.graph.tools")
    async def test_acceptable_score_skips_rebalance(self, mock_tools):
        """A score of 75 (above 50 threshold) should NOT trigger rebalance."""
        mock_tools.get_plan = AsyncMock(return_value=MOCK_PLAN)

        from app.agent.graph import rebalance_graph

        result = await rebalance_graph.ainvoke({
            "student_id": "stu-001",
            "trigger": "low_score",
            "trigger_details": {"score": 75, "topic_name": "Sorting"},
        })

        assert result["changes_needed"] is False
        assert result["new_plan"] is None
        # get_scores and regenerate_plan should NOT have been called
        mock_tools.get_scores.assert_not_called()
        mock_tools.regenerate_plan.assert_not_called()


# ── Test: Low score → rebalance ───────────────────────────────

class TestAgentLowScore:
    @pytest.mark.asyncio
    @patch("app.agent.graph.tools")
    async def test_low_score_triggers_rebalance(self, mock_tools):
        """A score of 35 (below 50) should trigger rebalance."""
        mock_tools.get_plan = AsyncMock(return_value=MOCK_PLAN)
        mock_tools.get_scores = AsyncMock(return_value=MOCK_SCORES)
        mock_tools.regenerate_plan = AsyncMock(return_value=MOCK_NEW_PLAN)

        from app.agent.graph import rebalance_graph

        result = await rebalance_graph.ainvoke({
            "student_id": "stu-001",
            "trigger": "low_score",
            "trigger_details": {"score": 35, "topic_name": "Trees"},
        })

        assert result["changes_needed"] is True
        assert "35" in result["explanation"]


# ── Test: New assignment far away → no rebalance ──────────────

class TestAgentNewAssignment:
    @pytest.mark.asyncio
    @patch("app.agent.graph.tools")
    async def test_far_assignment_skips_rebalance(self, mock_tools):
        """Assignment 20 days away (> 7 threshold) → no rebalance."""
        mock_tools.get_plan = AsyncMock(return_value=MOCK_PLAN)

        from app.agent.graph import rebalance_graph

        result = await rebalance_graph.ainvoke({
            "student_id": "stu-001",
            "trigger": "new_assignment",
            "trigger_details": {"days_until_due": 20},
        })

        assert result["changes_needed"] is False

    @pytest.mark.asyncio
    @patch("app.agent.graph.tools")
    async def test_imminent_assignment_triggers_rebalance(self, mock_tools):
        """Assignment 3 days away (≤ 7) → rebalance."""
        mock_tools.get_plan = AsyncMock(return_value=MOCK_PLAN)
        mock_tools.get_scores = AsyncMock(return_value=MOCK_SCORES)
        mock_tools.regenerate_plan = AsyncMock(return_value=MOCK_NEW_PLAN)

        from app.agent.graph import rebalance_graph

        result = await rebalance_graph.ainvoke({
            "student_id": "stu-001",
            "trigger": "new_assignment",
            "trigger_details": {"days_until_due": 3},
        })

        assert result["changes_needed"] is True
        assert "3 days" in result["explanation"]


# ── Test: Explanation content ─────────────────────────────────

class TestAgentExplanation:
    @pytest.mark.asyncio
    @patch("app.agent.graph.tools")
    async def test_explanation_includes_top_topics(self, mock_tools):
        """Explanation should mention the highest-priority topics."""
        mock_tools.get_plan = AsyncMock(return_value=MOCK_PLAN)
        mock_tools.get_scores = AsyncMock(return_value=MOCK_SCORES)
        mock_tools.regenerate_plan = AsyncMock(return_value=MOCK_NEW_PLAN)

        from app.agent.graph import rebalance_graph

        result = await rebalance_graph.ainvoke({
            "student_id": "stu-001",
            "trigger": "manual",
            "trigger_details": {},
        })

        assert "Linked Lists" in result["explanation"]
        assert "priority" in result["explanation"].lower()
