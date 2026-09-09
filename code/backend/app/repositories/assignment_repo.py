"""
Repository for the `assignments` table.

Pure CRUD — no validation, no business rules.
Assignments are deadline/urgency signals only — never used for mastery.
"""

from app.core.supabase_client import get_client


async def create(data: dict) -> dict:
    """INSERT a new assignment. Returns the created row."""
    async with get_client() as client:
        resp = await client.post("/assignments", json=data)
        resp.raise_for_status()
        return resp.json()[0]


async def get_all() -> list[dict]:
    """SELECT all assignments."""
    async with get_client() as client:
        resp = await client.get("/assignments", params={"select": "*"})
        resp.raise_for_status()
        return resp.json()


async def get_by_topic(topic_id: str) -> list[dict]:
    """SELECT all assignments for a given topic."""
    async with get_client() as client:
        resp = await client.get(
            "/assignments",
            params={
                "topic_id": f"eq.{topic_id}",
                "select": "*",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_by_id(assignment_id: str) -> dict | None:
    """SELECT a single assignment by ID."""
    async with get_client() as client:
        resp = await client.get(
            "/assignments",
            params={"id": f"eq.{assignment_id}", "select": "*"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def update(assignment_id: str, data: dict) -> dict | None:
    """UPDATE an assignment by ID."""
    async with get_client() as client:
        resp = await client.patch(
            "/assignments",
            params={"id": f"eq.{assignment_id}"},
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def delete(assignment_id: str) -> bool:
    """DELETE an assignment by ID."""
    async with get_client() as client:
        resp = await client.delete(
            "/assignments",
            params={"id": f"eq.{assignment_id}"},
        )
        resp.raise_for_status()
        return len(resp.json()) > 0
