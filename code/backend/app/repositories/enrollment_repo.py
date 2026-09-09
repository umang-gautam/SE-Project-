"""
Repository for the `enrollments` table.

Pure CRUD — no validation, no business rules.
"""

from app.core.supabase_client import get_client


async def create(data: dict) -> dict:
    """INSERT a new enrollment. Returns the created row."""
    async with get_client() as client:
        resp = await client.post("/enrollments", json=data)
        resp.raise_for_status()
        return resp.json()[0]


async def get_all() -> list[dict]:
    """SELECT all enrollments."""
    async with get_client() as client:
        resp = await client.get("/enrollments", params={"select": "*"})
        resp.raise_for_status()
        return resp.json()


async def get_by_student(student_id: str) -> list[dict]:
    """SELECT all enrollments for a given student."""
    async with get_client() as client:
        resp = await client.get(
            "/enrollments",
            params={
                "student_id": f"eq.{student_id}",
                "select": "*",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_by_id(enrollment_id: str) -> dict | None:
    """SELECT a single enrollment by ID."""
    async with get_client() as client:
        resp = await client.get(
            "/enrollments",
            params={"id": f"eq.{enrollment_id}", "select": "*"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def delete(enrollment_id: str) -> bool:
    """DELETE an enrollment by ID."""
    async with get_client() as client:
        resp = await client.delete(
            "/enrollments",
            params={"id": f"eq.{enrollment_id}"},
        )
        resp.raise_for_status()
        return len(resp.json()) > 0
