"""
LangGraph agent — state machine for adaptive study plan rebalancing.

Node flow:
  detect_change → re_score → re_plan → explain_decision → END
                ↘ (no change needed) → END

Every node is a deterministic Python function for now.
An LLM-powered explanation node is a documented future upgrade.

The graph ONLY calls tools from agent/tools.py, which wrap services/.
It has no access to repositories/ or the database.
"""

from __future__ import annotations

from typing import TypedDict, Literal
from datetime import date

from langgraph.graph import StateGraph, END

from app.agent import tools


# ══════════════════════════════════════════════════════════════
# State definition
# ══════════════════════════════════════════════════════════════

class AgentState(TypedDict, total=False):
    """Shared state passed between graph nodes."""

    # Input
    student_id: str
    trigger: str  # "missed_session" | "low_score" | "new_assignment" | "manual"
    trigger_details: dict  # e.g. {"session_id": "...", "status": "missed"}

    # Intermediate
    current_plan: dict | None
    scores: list[dict]
    changes_needed: bool
    reason: str  # why rebalancing is/isn't needed

    # Output
    new_plan: dict | None
    explanation: str


# ══════════════════════════════════════════════════════════════
# Node functions
# ══════════════════════════════════════════════════════════════

async def detect_change(state: AgentState) -> dict:
    """
    Node 1: Examine the trigger and current state to decide if
    rebalancing is needed.

    Trigger conditions:
      - "missed_session": a session was marked missed → rebalance
      - "low_score": a new PerformanceRecord is below 50 → rebalance
      - "new_assignment": a new assignment with ≤7 days to due → rebalance
      - "manual": explicit user request → always rebalance
    """
    trigger = state.get("trigger", "manual")
    details = state.get("trigger_details", {})

    # Fetch current plan
    student_id = state["student_id"]
    current_plan = await tools.get_plan(student_id)

    if trigger == "missed_session":
        return {
            "current_plan": current_plan,
            "changes_needed": True,
            "reason": f"Session {details.get('session_id', '?')} was missed — rebalancing to redistribute time.",
        }

    elif trigger == "low_score":
        score_val = details.get("score", 0)
        topic_name = details.get("topic_name", "a topic")
        return {
            "current_plan": current_plan,
            "changes_needed": score_val < 50,
            "reason": (
                f"New score of {score_val} on {topic_name} — "
                + ("needs more study time." if score_val < 50 else "score is acceptable, no rebalance needed.")
            ),
        }

    elif trigger == "new_assignment":
        days_until = details.get("days_until_due", 30)
        return {
            "current_plan": current_plan,
            "changes_needed": days_until <= 7,
            "reason": (
                f"New assignment due in {days_until} days — "
                + ("urgent, rebalancing." if days_until <= 7 else "not urgent yet.")
            ),
        }

    else:  # "manual" or unknown
        return {
            "current_plan": current_plan,
            "changes_needed": True,
            "reason": "Manual rebalance requested.",
        }


async def re_score(state: AgentState) -> dict:
    """
    Node 2: Re-score all enrolled topics with latest data.
    """
    scores = await tools.get_scores(state["student_id"])
    return {"scores": scores}


async def re_plan(state: AgentState) -> dict:
    """
    Node 3: Generate a new plan based on updated scores.

    Uses the remaining days in the current plan's date range,
    or defaults to 7 days if no current plan exists.
    """
    current_plan = state.get("current_plan")

    # Determine time budget from current plan or defaults
    if current_plan:
        end_date = current_plan.get("end_date", "")
        if isinstance(end_date, str) and end_date:
            remaining_days = (date.fromisoformat(end_date) - date.today()).days
            remaining_days = max(1, remaining_days)
        else:
            remaining_days = 7

        # Estimate hours/day from existing sessions
        sessions = current_plan.get("sessions", [])
        if sessions:
            total_minutes = sum(s.get("duration_minutes", 45) for s in sessions)
            hours_per_day = min(6, max(1, total_minutes / (remaining_days * 60)))
        else:
            hours_per_day = 2
    else:
        remaining_days = 7
        hours_per_day = 2

    new_plan = await tools.regenerate_plan(
        student_id=state["student_id"],
        hours_per_day=hours_per_day,
        num_days=remaining_days,
    )
    return {"new_plan": new_plan}


async def explain_decision(state: AgentState) -> dict:
    """
    Node 4: Generate a human-readable explanation of the rebalance.

    Currently deterministic. Future upgrade: use an LLM for
    natural language explanations.
    """
    reason = state.get("reason", "Unknown trigger")
    scores = state.get("scores", [])
    new_plan = state.get("new_plan")

    # Build explanation
    parts = [f"Rebalance triggered: {reason}"]

    if scores:
        top_3 = scores[:3]
        parts.append("Top priority topics:")
        for t in top_3:
            parts.append(
                f"  • {t['topic_name']} — priority {t['priority']:.0f} "
                f"(mastery {t['mastery']:.0%}, urgency {t['urgency']:.0%})"
            )

    if new_plan:
        session_count = len(new_plan.get("sessions", []))
        parts.append(f"New plan created with {session_count} study sessions.")

    return {"explanation": "\n".join(parts)}


async def no_change_needed(state: AgentState) -> dict:
    """Terminal node when no rebalance is needed."""
    return {
        "explanation": f"No rebalance needed. {state.get('reason', '')}",
        "new_plan": None,
    }


# ══════════════════════════════════════════════════════════════
# Routing function
# ══════════════════════════════════════════════════════════════

def should_rebalance(state: AgentState) -> Literal["re_score", "no_change"]:
    """Conditional edge: proceed with rebalancing or stop."""
    if state.get("changes_needed", False):
        return "re_score"
    return "no_change"


# ══════════════════════════════════════════════════════════════
# Graph construction
# ══════════════════════════════════════════════════════════════

def build_graph() -> StateGraph:
    """
    Build the rebalancing agent graph.

    Flow:
      START → detect_change →[changes_needed?]→ re_score → re_plan → explain → END
                              ↘ [no]→ no_change → END
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("detect_change", detect_change)
    graph.add_node("re_score", re_score)
    graph.add_node("re_plan", re_plan)
    graph.add_node("explain_decision", explain_decision)
    graph.add_node("no_change", no_change_needed)

    # Set entry point
    graph.set_entry_point("detect_change")

    # Add conditional edge from detect_change
    graph.add_conditional_edges(
        "detect_change",
        should_rebalance,
        {
            "re_score": "re_score",
            "no_change": "no_change",
        },
    )

    # Linear flow for the rebalance path
    graph.add_edge("re_score", "re_plan")
    graph.add_edge("re_plan", "explain_decision")
    graph.add_edge("explain_decision", END)

    # Terminal for no-change path
    graph.add_edge("no_change", END)

    return graph


# Pre-compiled graph instance
rebalance_graph = build_graph().compile()
