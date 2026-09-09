"""
Repository for the `students` table.

Pure CRUD — no validation, no business rules.
Every function opens an httpx client, makes one REST call, and returns
the raw response data (a list of dicts or a single dict).
"""

from app.core.supabase_client import get_client


async def create(data: dict) -> dict:
    """INSERT a new student. Returns the created row."""
    async with get_client() as client:
        resp = await client.post("/students", json=data)
        resp.raise_for_status()
        return resp.json()[0]


async def get_all() -> list[dict]:
    """SELECT all students."""
    async with get_client() as client:
        resp = await client.get("/students", params={"select": "*"})
        resp.raise_for_status()
        return resp.json()


async def get_by_id(student_id: str) -> dict | None:
    """SELECT a single student by ID. Returns None if not found."""
    async with get_client() as client:
        resp = await client.get(
            "/students",
            params={"id": f"eq.{student_id}", "select": "*"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def update(student_id: str, data: dict) -> dict | None:
    """UPDATE a student by ID. Returns the updated row or None."""
    async with get_client() as client:
        resp = await client.patch(
            "/students",
            params={"id": f"eq.{student_id}"},
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def delete(student_id: str) -> bool:
    """DELETE a student by ID. Returns True if a row was deleted."""
    async with get_client() as client:
        resp = await client.delete(
            "/students",
            params={"id": f"eq.{student_id}"},
        )
        resp.raise_for_status()
        return len(resp.json()) > 0
