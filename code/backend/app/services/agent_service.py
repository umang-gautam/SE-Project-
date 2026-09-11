"""
Agent service — entry point for triggering the LangGraph rebalance agent.

This is the service that routes/agent.py calls. It constructs the
initial state and invokes the compiled graph.
"""

from app.agent.graph import rebalance_graph, AgentState


async def trigger_rebalance(
    student_id: str,
    trigger: str = "manual",
    trigger_details: dict | None = None,
) -> dict:
    """
    Run the rebalancing agent for a student.

    Args:
        student_id: Which student to rebalance for.
        trigger: What caused the rebalance — one of:
                 "missed_session", "low_score", "new_assignment", "manual"
        trigger_details: Optional dict with context, e.g.
                         {"session_id": "...", "score": 35, "topic_name": "Trees"}

    Returns:
        A dict with:
          - explanation: human-readable summary of what happened
          - new_plan: the new plan dict (or None if no rebalance was needed)
          - changes_needed: whether a rebalance was performed
    """
    initial_state: AgentState = {
        "student_id": student_id,
        "trigger": trigger,
        "trigger_details": trigger_details or {},
    }

    # Run the graph to completion
    final_state = await rebalance_graph.ainvoke(initial_state)

    return {
        "student_id": student_id,
        "trigger": trigger,
        "changes_needed": final_state.get("changes_needed", False),
        "explanation": final_state.get("explanation", ""),
        "new_plan": final_state.get("new_plan"),
    }
