"""
Study plan generation service.

Contains:
  1. get_student_topic_scores() — orchestrates data fetching + scoring
  2. allocate_sessions()        — PURE function: scored topics + budget → session list
  3. generate_plan()            — end-to-end: score → allocate → save to DB

The allocation logic is deliberately pure (no I/O) so it can be
unit-tested without mocking anything — same strategy as scoring_service.
"""

from datetime import date, timedelta

from app.services import scoring_service
from app.repositories import (
    enrollment_repo,
    subject_repo,
    topic_repo,
    assignment_repo,
    performance_repo,
    study_plan_repo,
    study_session_repo,
)


# ── Constants ─────────────────────────────────────────────────

MIN_SESSION_MINUTES: int = 30
MAX_SESSION_MINUTES: int = 60
TARGET_SESSION_MINUTES: int = 45  # ideal session length for splitting


# ══════════════════════════════════════════════════════════════
# 1. Scoring orchestrator (async — fetches data, calls pure scoring)
# ══════════════════════════════════════════════════════════════

async def get_student_topic_scores(
    student_id: str,
    today: date | None = None,
) -> list[dict]:
    """
    Fetch all enrolled topics for a student, score each one, and
    return a list sorted by priority descending.

    Each item in the returned list contains:
      topic_id, topic_name, subject_id, subject_name,
      mastery, urgency, priority
    """
    if today is None:
        today = date.today()

    # 1. Get the student's enrollments → subject IDs
    enrollments = await enrollment_repo.get_by_student(student_id)
    if not enrollments:
        return []

    scored_topics = []

    for enrollment in enrollments:
        subject_id = enrollment["subject_id"]

        # 2. Get subject info
        subject = await subject_repo.get_by_id(subject_id)
        if not subject:
            continue

        # 3. Get all topics for this subject
        topics = await topic_repo.get_by_subject(subject_id)

        for topic in topics:
            topic_id = topic["id"]

            # 4. Fetch raw data for scoring
            perf_records = await performance_repo.get_by_student_and_topic(
                student_id, topic_id
            )
            scores = [r["score"] for r in perf_records]

            assignments = await assignment_repo.get_by_topic(topic_id)
            due_dates = [
                date.fromisoformat(a["due_date"])
                if isinstance(a["due_date"], str)
                else a["due_date"]
                for a in assignments
            ]

            # 5. Score using pure functions
            result = scoring_service.score_topic(scores, due_dates, today)

            scored_topics.append({
                "topic_id": topic_id,
                "topic_name": topic["name"],
                "subject_id": subject_id,
                "subject_name": subject["name"],
                **result,  # mastery, urgency, priority
            })

    # Sort by priority descending (most important first)
    scored_topics.sort(key=lambda t: t["priority"], reverse=True)
    return scored_topics


# ══════════════════════════════════════════════════════════════
# 2. Session allocation (PURE — no I/O, trivially testable)
# ══════════════════════════════════════════════════════════════

def allocate_sessions(
    scored_topics: list[dict],
    start_date: date,
    num_days: int,
    minutes_per_day: int,
) -> list[dict]:
    """
    Allocate study sessions across days based on topic priorities.

    Algorithm:
      1. Total time = minutes_per_day × num_days
      2. Each topic gets time proportional to its priority share
      3. Topics with < MIN_SESSION_MINUTES of allocated time are skipped
      4. Allocated time is split into 30–60 minute sessions
      5. Sessions are distributed across days round-robin

    Returns a list of session dicts (no IDs — those come from the DB).
    """
    if not scored_topics or num_days <= 0 or minutes_per_day <= 0:
        return []

    total_minutes = minutes_per_day * num_days

    # Filter to topics with non-zero priority
    active_topics = [t for t in scored_topics if t["priority"] > 0]
    if not active_topics:
        return []

    total_priority = sum(t["priority"] for t in active_topics)
    if total_priority == 0:
        return []

    sessions = []
    day_usage = [0] * num_days  # track minutes used per day

    for topic in active_topics:
        # Proportional time allocation
        topic_minutes = total_minutes * (topic["priority"] / total_priority)

        if topic_minutes < MIN_SESSION_MINUTES:
            continue

        # Split into sessions of TARGET_SESSION_MINUTES
        num_sessions = max(1, round(topic_minutes / TARGET_SESSION_MINUTES))
        session_duration = round(topic_minutes / num_sessions)
        session_duration = max(MIN_SESSION_MINUTES, min(MAX_SESSION_MINUTES, session_duration))

        # Distribute sessions across days (pick the least-used day first)
        for _ in range(num_sessions):
            # Find the day with the most remaining capacity
            best_day = min(range(num_days), key=lambda d: day_usage[d])

            if day_usage[best_day] + session_duration > minutes_per_day + 5:
                # Allow 5-min grace, but skip if truly over budget
                continue

            session_date = start_date + timedelta(days=best_day)
            sessions.append({
                "topic_id": topic["topic_id"],
                "date": session_date.isoformat(),
                "duration_minutes": session_duration,
                "status": "pending",
            })
            day_usage[best_day] += session_duration

    return sessions


# ══════════════════════════════════════════════════════════════
# 3. End-to-end plan generation (async — orchestrates everything)
# ══════════════════════════════════════════════════════════════

async def generate_plan(
    student_id: str,
    hours_per_day: float,
    num_days: int,
    start_date: date | None = None,
) -> dict:
    """
    Generate a complete study plan for a student.

    1. Score all enrolled topics
    2. Allocate sessions based on time budget
    3. Save StudyPlan + StudySessions to database
    4. Return the plan with sessions and scores
    """
    if start_date is None:
        start_date = date.today()

    end_date = start_date + timedelta(days=num_days - 1)
    minutes_per_day = int(hours_per_day * 60)

    # Step 1: Score topics
    scored_topics = await get_student_topic_scores(student_id, today=start_date)

    # Step 2: Allocate sessions (pure function)
    session_dicts = allocate_sessions(
        scored_topics, start_date, num_days, minutes_per_day
    )

    # Step 3: Save plan to database
    plan = await study_plan_repo.create({
        "student_id": student_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    })

    # Step 4: Save sessions with the plan_id
    saved_sessions = []
    if session_dicts:
        for s in session_dicts:
            s["plan_id"] = plan["id"]
        saved_sessions = await study_session_repo.create_many(session_dicts)

    return {
        "plan_id": plan["id"],
        "student_id": student_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "sessions": saved_sessions,
        "topic_scores": scored_topics,
    }
