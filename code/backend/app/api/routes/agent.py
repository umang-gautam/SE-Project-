"""
Agent route — POST /agent/rebalance.

Triggers the LangGraph agent to evaluate whether a student's
study plan needs rebalancing and, if so, generate a new one.
"""

from fastapi import APIRouter, status
from app.services import agent_service
from app.schemas.agent import RebalanceRequest, RebalanceResponse

router = APIRouter()


@router.post("/rebalance", response_model=RebalanceResponse, status_code=status.HTTP_200_OK)
async def rebalance(req: RebalanceRequest):
    """
    Trigger the rebalancing agent.

    The agent will:
    1. Detect whether the trigger warrants a rebalance
    2. Re-score all enrolled topics if needed
    3. Generate a new study plan
    4. Return an explanation of what changed and why
    """
    result = await agent_service.trigger_rebalance(
        student_id=req.student_id,
        trigger=req.trigger,
        trigger_details=req.trigger_details,
    )
    return result
