"""
Tools exposed to the LangGraph agent.

ARCHITECTURAL CONSTRAINT (non-negotiable):
  These tools wrap services/ functions ONLY.
  The agent has NO import path to repositories/ or supabase_client.
  Every action the agent takes goes through the same business logic
  that a human-triggered API call would go through.

Each tool is an async function that takes simple arguments and
returns a dict. The agent graph calls these through the state machine.
"""

from datetime import date

from app.services import (
    plan_service,
    study_plan_service,
    study_session_service,
    performance_service,
)


async def get_scores(student_id: str) -> list[dict]:
    """
    Fetch and score all enrolled topics for a student.

    Returns a list of dicts with:
      topic_id, topic_name, subject_name, mastery, urgency, priority
    Sorted by priority descending.
    """
    return await plan_service.get_student_topic_scores(student_id)


async def get_plan(student_id: str) -> dict | None:
    """
    Fetch the most recent study plan for a student.

    Returns the plan dict with its sessions, or None if no plan exists.
    """
    plans = await study_plan_service.get_study_plans_by_student(student_id)
    if not plans:
        return None

    # Most recent plan (already sorted by start_date desc)
    plan = plans[0]
    plan_id = plan["id"]

    # Fetch sessions for this plan
    from app.services import study_session_service
    sessions = await study_session_service.get_sessions_by_plan(plan_id)
    plan["sessions"] = sessions
    return plan


async def update_session_status(session_id: str, status: str) -> dict | None:
    """
    Mark a study session as done, missed, or pending.

    This is the tool the agent uses to log session outcomes.
    The status change goes through the service layer, which
    enforces the valid status enum.
    """
    return await study_session_service.update_study_session(
        session_id, {"status": status}
    )


async def regenerate_plan(
    student_id: str,
    hours_per_day: float,
    num_days: int,
    start_date: str | None = None,
) -> dict:
    """
    Generate a new study plan for the student.

    This wraps plan_service.generate_plan — the same function
    the POST /study-plans/generate endpoint calls.
    """
    sd = date.fromisoformat(start_date) if start_date else None
    return await plan_service.generate_plan(
        student_id=student_id,
        hours_per_day=hours_per_day,
        num_days=num_days,
        start_date=sd,
    )
