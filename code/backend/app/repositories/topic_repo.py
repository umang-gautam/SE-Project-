"""
Repository for the `topics` table.

Pure CRUD — no validation, no business rules.
"""

from app.core.supabase_client import get_client


async def create(data: dict) -> dict:
    """INSERT a new topic. Returns the created row."""
    async with get_client() as client:
        resp = await client.post("/topics", json=data)
        resp.raise_for_status()
        return resp.json()[0]


async def get_all() -> list[dict]:
    """SELECT all topics."""
    async with get_client() as client:
        resp = await client.get("/topics", params={"select": "*"})
        resp.raise_for_status()
        return resp.json()


async def get_by_subject(subject_id: str) -> list[dict]:
    """SELECT all topics belonging to a subject."""
    async with get_client() as client:
        resp = await client.get(
            "/topics",
            params={
                "subject_id": f"eq.{subject_id}",
                "select": "*",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_by_id(topic_id: str) -> dict | None:
    """SELECT a single topic by ID."""
    async with get_client() as client:
        resp = await client.get(
            "/topics",
            params={"id": f"eq.{topic_id}", "select": "*"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def update(topic_id: str, data: dict) -> dict | None:
    """UPDATE a topic by ID. Returns the updated row or None."""
    async with get_client() as client:
        resp = await client.patch(
            "/topics",
            params={"id": f"eq.{topic_id}"},
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def delete(topic_id: str) -> bool:
    """DELETE a topic by ID."""
    async with get_client() as client:
        resp = await client.delete(
            "/topics",
            params={"id": f"eq.{topic_id}"},
        )
        resp.raise_for_status()
        return len(resp.json()) > 0
