"""Pydantic schemas for the agent rebalance endpoint."""

from pydantic import BaseModel, Field


class RebalanceRequest(BaseModel):
    """Input for POST /agent/rebalance."""
    student_id: str
    trigger: str = Field(
        default="manual",
        description="What caused the rebalance: missed_session, low_score, new_assignment, manual",
    )
    trigger_details: dict = Field(
        default_factory=dict,
        description="Optional context, e.g. {session_id, score, topic_name, days_until_due}",
    )


class RebalanceResponse(BaseModel):
    """Output of POST /agent/rebalance."""
    student_id: str
    trigger: str
    changes_needed: bool
    explanation: str
    new_plan: dict | None = None
