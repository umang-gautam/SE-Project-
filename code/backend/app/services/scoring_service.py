"""
Scoring engine — pure functions for computing topic priority.

ALL functions in this module are pure: they take data in, return numbers
out, and never touch I/O (no database calls, no HTTP, no disk).
This makes them trivially unit-testable.

Scoring formula:
  mastery   = average(scores) / 100          → 0.0 (weak) to 1.0 (strong)
  urgency   = time-decay from nearest due_date → 0.0 (far) to 1.0 (imminent)
  priority  = 100 × (w1 × (1 − mastery) + w2 × urgency)  → 0 to 100

Higher priority = study this topic first.
"""

from datetime import date


# ── Configurable weights (must sum to 1.0) ────────────────────
MASTERY_WEIGHT: float = 0.6
URGENCY_WEIGHT: float = 0.4

# How many days out we consider "not urgent at all".
# Assignments further than this many days away get urgency ≈ 0.
URGENCY_HORIZON_DAYS: int = 30


def compute_mastery(scores: list[float]) -> float:
    """
    Average of raw scores (each 0–100), normalized to 0.0–1.0.

    Returns 0.0 if there are no scores (no data = no mastery).

    >>> compute_mastery([80, 60, 70])
    0.7
    >>> compute_mastery([])
    0.0
    """
    if not scores:
        return 0.0
    return sum(scores) / (len(scores) * 100)


def compute_urgency(
    due_dates: list[date],
    today: date | None = None,
) -> float:
    """
    Urgency based on the nearest due_date.

    - Past-due or due today → 1.0 (maximum urgency)
    - URGENCY_HORIZON_DAYS or more days away → 0.0
    - In between → linear interpolation

    Returns 0.0 if there are no due dates (no deadlines = no urgency).

    >>> from datetime import date
    >>> compute_urgency([date(2025, 1, 10)], today=date(2025, 1, 10))
    1.0
    >>> compute_urgency([date(2025, 2, 10)], today=date(2025, 1, 10))
    0.0
    >>> compute_urgency([], today=date(2025, 1, 10))
    0.0
    """
    if not due_dates:
        return 0.0

    if today is None:
        today = date.today()

    # Find the closest deadline
    nearest = min(due_dates)
    days_remaining = (nearest - today).days

    if days_remaining <= 0:
        return 1.0
    if days_remaining >= URGENCY_HORIZON_DAYS:
        return 0.0

    # Linear decay: 1.0 at day 0 → 0.0 at URGENCY_HORIZON_DAYS
    return 1.0 - (days_remaining / URGENCY_HORIZON_DAYS)


def compute_priority(
    mastery_norm: float,
    urgency_norm: float,
    w_mastery: float = MASTERY_WEIGHT,
    w_urgency: float = URGENCY_WEIGHT,
) -> float:
    """
    Weighted priority score, 0–100.

    priority = 100 × (w_mastery × (1 − mastery) + w_urgency × urgency)

    The (1 − mastery) flip means: lower mastery → higher priority.

    >>> compute_priority(mastery_norm=0.3, urgency_norm=0.8)
    74.0
    >>> compute_priority(mastery_norm=1.0, urgency_norm=0.0)
    0.0
    """
    raw = w_mastery * (1.0 - mastery_norm) + w_urgency * urgency_norm
    return round(raw * 100, 2)


def score_topic(
    scores: list[float],
    due_dates: list[date],
    today: date | None = None,
    w_mastery: float = MASTERY_WEIGHT,
    w_urgency: float = URGENCY_WEIGHT,
) -> dict:
    """
    Convenience: compute all three scores for a single topic.

    Returns a dict with mastery, urgency, and priority — ready to
    be serialized to JSON by a route handler.

    >>> result = score_topic([80, 60], [date(2025, 1, 15)], today=date(2025, 1, 10))
    >>> result["mastery"]
    0.7
    """
    mastery = compute_mastery(scores)
    urgency = compute_urgency(due_dates, today)
    priority = compute_priority(mastery, urgency, w_mastery, w_urgency)
    return {
        "mastery": mastery,
        "urgency": round(urgency, 4),
        "priority": priority,
    }
