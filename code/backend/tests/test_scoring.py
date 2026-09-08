"""
Unit tests for the scoring engine.

These tests are PURE — no mocking, no async, no database.
The scoring functions take numbers in and return numbers out,
so we just verify the math is correct.
"""

import pytest
from datetime import date

from app.services.scoring_service import (
    compute_mastery,
    compute_urgency,
    compute_priority,
    score_topic,
    MASTERY_WEIGHT,
    URGENCY_WEIGHT,
    URGENCY_HORIZON_DAYS,
)


# ── compute_mastery ───────────────────────────────────────────

class TestComputeMastery:
    def test_average_of_scores_normalized(self):
        """[80, 60, 70] → average 70 → normalized 0.7"""
        assert compute_mastery([80, 60, 70]) == pytest.approx(0.7)

    def test_perfect_scores(self):
        assert compute_mastery([100, 100, 100]) == pytest.approx(1.0)

    def test_zero_scores(self):
        assert compute_mastery([0, 0, 0]) == pytest.approx(0.0)

    def test_single_score(self):
        assert compute_mastery([50]) == pytest.approx(0.5)

    def test_empty_scores_returns_zero(self):
        """No data = no mastery (student hasn't been tested yet)."""
        assert compute_mastery([]) == 0.0

    def test_mixed_scores(self):
        """[100, 0] → average 50 → normalized 0.5"""
        assert compute_mastery([100, 0]) == pytest.approx(0.5)


# ── compute_urgency ───────────────────────────────────────────

class TestComputeUrgency:
    TODAY = date(2025, 1, 15)

    def test_due_today(self):
        """Due today → maximum urgency."""
        assert compute_urgency([date(2025, 1, 15)], today=self.TODAY) == 1.0

    def test_past_due(self):
        """Already past → still maximum urgency."""
        assert compute_urgency([date(2025, 1, 10)], today=self.TODAY) == 1.0

    def test_far_future(self):
        """Due 30+ days away → zero urgency."""
        far = date(2025, 2, 20)  # 36 days from Jan 15
        assert compute_urgency([far], today=self.TODAY) == 0.0

    def test_exactly_at_horizon(self):
        """Due exactly URGENCY_HORIZON_DAYS away → zero urgency."""
        boundary = date(2025, 2, 14)  # exactly 30 days from Jan 15
        assert compute_urgency([boundary], today=self.TODAY) == 0.0

    def test_halfway(self):
        """Due 15 days away (half of 30-day horizon) → 0.5 urgency."""
        halfway = date(2025, 1, 30)  # 15 days from Jan 15
        assert compute_urgency([halfway], today=self.TODAY) == pytest.approx(0.5)

    def test_one_day_away(self):
        """Due tomorrow → very high urgency."""
        tomorrow = date(2025, 1, 16)
        expected = 1.0 - (1 / URGENCY_HORIZON_DAYS)
        assert compute_urgency([tomorrow], today=self.TODAY) == pytest.approx(expected)

    def test_multiple_dates_uses_nearest(self):
        """Multiple assignments → urgency based on the closest deadline."""
        dates = [date(2025, 2, 15), date(2025, 1, 20), date(2025, 3, 1)]
        # Nearest is Jan 20 → 5 days away → 1 - 5/30 = 0.8333...
        expected = 1.0 - (5 / URGENCY_HORIZON_DAYS)
        assert compute_urgency(dates, today=self.TODAY) == pytest.approx(expected)

    def test_no_due_dates_returns_zero(self):
        """No assignments → no urgency."""
        assert compute_urgency([], today=self.TODAY) == 0.0


# ── compute_priority ──────────────────────────────────────────

class TestComputePriority:
    def test_weak_and_urgent(self):
        """Low mastery (0.2) + high urgency (0.9) → high priority."""
        result = compute_priority(0.2, 0.9)
        # 100 * (0.6 * 0.8 + 0.4 * 0.9) = 100 * (0.48 + 0.36) = 84.0
        assert result == pytest.approx(84.0)

    def test_strong_and_not_urgent(self):
        """High mastery (0.95) + low urgency (0.1) → low priority."""
        result = compute_priority(0.95, 0.1)
        # 100 * (0.6 * 0.05 + 0.4 * 0.1) = 100 * (0.03 + 0.04) = 7.0
        assert result == pytest.approx(7.0)

    def test_perfect_mastery_no_urgency(self):
        """Know everything, nothing due → priority = 0."""
        assert compute_priority(1.0, 0.0) == 0.0

    def test_zero_mastery_full_urgency(self):
        """Know nothing, deadline today → priority = 100."""
        assert compute_priority(0.0, 1.0) == 100.0

    def test_custom_weights(self):
        """Override default weights (e.g., urgency-heavy)."""
        result = compute_priority(0.5, 0.5, w_mastery=0.3, w_urgency=0.7)
        # 100 * (0.3 * 0.5 + 0.7 * 0.5) = 100 * (0.15 + 0.35) = 50.0
        assert result == pytest.approx(50.0)

    def test_output_range_never_exceeds_100(self):
        """Worst case: mastery=0, urgency=1 → exactly 100."""
        assert compute_priority(0.0, 1.0) <= 100.0

    def test_output_range_never_below_zero(self):
        """Best case: mastery=1, urgency=0 → exactly 0."""
        assert compute_priority(1.0, 0.0) >= 0.0


# ── score_topic (integration of all three) ────────────────────

class TestScoreTopic:
    TODAY = date(2025, 1, 15)

    def test_full_pipeline(self):
        """End-to-end: scores + due_dates → mastery + urgency + priority."""
        result = score_topic(
            scores=[80, 60],
            due_dates=[date(2025, 1, 20)],
            today=self.TODAY,
        )
        # mastery = avg(80,60)/100 = 0.7
        assert result["mastery"] == pytest.approx(0.7)
        # urgency = 1 - 5/30 = 0.8333...
        assert result["urgency"] == pytest.approx(0.8333, abs=0.001)
        # priority = 100 * (0.6 * 0.3 + 0.4 * 0.8333) = 100 * (0.18 + 0.3333) = 51.33
        assert result["priority"] == pytest.approx(51.33, abs=0.1)

    def test_no_data_at_all(self):
        """New topic: no scores, no assignments → priority based only on mastery=0."""
        result = score_topic(scores=[], due_dates=[], today=self.TODAY)
        assert result["mastery"] == 0.0
        assert result["urgency"] == 0.0
        # priority = 100 * (0.6 * 1.0 + 0.4 * 0.0) = 60.0
        assert result["priority"] == pytest.approx(60.0)

    def test_result_contains_all_keys(self):
        result = score_topic([50], [date(2025, 1, 20)], today=self.TODAY)
        assert "mastery" in result
        assert "urgency" in result
        assert "priority" in result
