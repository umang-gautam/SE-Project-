"""
Repository for the `subjects` table.

Pure CRUD — no validation, no business rules.
"""

from app.core.supabase_client import get_client


async def create(data: dict) -> dict:
    """INSERT a new subject. Returns the created row."""
    async with get_client() as client:
        resp = await client.post("/subjects", json=data)
        resp.raise_for_status()
        return resp.json()[0]


async def get_all() -> list[dict]:
    """SELECT all subjects."""
    async with get_client() as client:
        resp = await client.get("/subjects", params={"select": "*"})
        resp.raise_for_status()
        return resp.json()


async def get_by_id(subject_id: str) -> dict | None:
    """SELECT a single subject by ID. Returns None if not found."""
    async with get_client() as client:
        resp = await client.get(
            "/subjects",
            params={"id": f"eq.{subject_id}", "select": "*"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def update(subject_id: str, data: dict) -> dict | None:
    """UPDATE a subject by ID. Returns the updated row or None."""
    async with get_client() as client:
        resp = await client.patch(
            "/subjects",
            params={"id": f"eq.{subject_id}"},
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def delete(subject_id: str) -> bool:
    """DELETE a subject by ID. Returns True if a row was deleted."""
    async with get_client() as client:
        resp = await client.delete(
            "/subjects",
            params={"id": f"eq.{subject_id}"},
        )
        resp.raise_for_status()
        return len(resp.json()) > 0
