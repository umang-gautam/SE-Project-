"""
Repository for the `study_sessions` table.

Pure CRUD — no validation, no business rules.
Sessions are the individual study blocks within a StudyPlan.
Kept separate so the agent can rebalance at session grain without
rebuilding the whole plan.
"""

from app.core.supabase_client import get_client


async def create(data: dict) -> dict:
    """INSERT a new study session. Returns the created row."""
    async with get_client() as client:
        resp = await client.post("/study_sessions", json=data)
        resp.raise_for_status()
        return resp.json()[0]


async def create_many(rows: list[dict]) -> list[dict]:
    """INSERT multiple study sessions at once. Returns the created rows."""
    async with get_client() as client:
        resp = await client.post("/study_sessions", json=rows)
        resp.raise_for_status()
        return resp.json()


async def get_by_plan(plan_id: str) -> list[dict]:
    """SELECT all sessions for a study plan, ordered by date."""
    async with get_client() as client:
        resp = await client.get(
            "/study_sessions",
            params={
                "plan_id": f"eq.{plan_id}",
                "select": "*",
                "order": "date.asc,duration_minutes.desc",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_by_id(session_id: str) -> dict | None:
    """SELECT a single study session by ID."""
    async with get_client() as client:
        resp = await client.get(
            "/study_sessions",
            params={"id": f"eq.{session_id}", "select": "*"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def update(session_id: str, data: dict) -> dict | None:
    """UPDATE a study session by ID (e.g., mark status as done/missed)."""
    async with get_client() as client:
        resp = await client.patch(
            "/study_sessions",
            params={"id": f"eq.{session_id}"},
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def delete_by_plan(plan_id: str) -> list[dict]:
    """DELETE all sessions for a plan (used when regenerating a plan)."""
    async with get_client() as client:
        resp = await client.delete(
            "/study_sessions",
            params={"plan_id": f"eq.{plan_id}"},
        )
        resp.raise_for_status()
        return resp.json()


async def delete(session_id: str) -> bool:
    """DELETE a single study session by ID."""
    async with get_client() as client:
        resp = await client.delete(
            "/study_sessions",
            params={"id": f"eq.{session_id}"},
        )
        resp.raise_for_status()
        return len(resp.json()) > 0
