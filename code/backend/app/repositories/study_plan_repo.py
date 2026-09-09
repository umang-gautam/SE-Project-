"""
Repository for the `study_plans` table.

Pure CRUD — no validation, no business rules.
A StudyPlan is an umbrella container; individual blocks live in study_sessions.
"""

from app.core.supabase_client import get_client


async def create(data: dict) -> dict:
    """INSERT a new study plan. Returns the created row."""
    async with get_client() as client:
        resp = await client.post("/study_plans", json=data)
        resp.raise_for_status()
        return resp.json()[0]


async def get_by_student(student_id: str) -> list[dict]:
    """SELECT all study plans for a student, newest first."""
    async with get_client() as client:
        resp = await client.get(
            "/study_plans",
            params={
                "student_id": f"eq.{student_id}",
                "select": "*",
                "order": "start_date.desc",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_by_id(plan_id: str) -> dict | None:
    """SELECT a single study plan by ID."""
    async with get_client() as client:
        resp = await client.get(
            "/study_plans",
            params={"id": f"eq.{plan_id}", "select": "*"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def update(plan_id: str, data: dict) -> dict | None:
    """UPDATE a study plan by ID."""
    async with get_client() as client:
        resp = await client.patch(
            "/study_plans",
            params={"id": f"eq.{plan_id}"},
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


async def delete(plan_id: str) -> bool:
    """DELETE a study plan by ID (cascades to sessions)."""
    async with get_client() as client:
        resp = await client.delete(
            "/study_plans",
            params={"id": f"eq.{plan_id}"},
        )
        resp.raise_for_status()
        return len(resp.json()) > 0
