"""
Repository for the `performance_records` table.

Pure CRUD — no validation, no business rules.
Multiple rows per student+topic over time — aggregation happens in services.
"""

from app.core.supabase_client import get_client


async def create(data: dict) -> dict:
    """INSERT a new performance record. Returns the created row."""
    async with get_client() as client:
        resp = await client.post("/performance_records", json=data)
        resp.raise_for_status()
        return resp.json()[0]


async def get_by_student(student_id: str) -> list[dict]:
    """SELECT all performance records for a student (across all topics)."""
    async with get_client() as client:
        resp = await client.get(
            "/performance_records",
            params={
                "student_id": f"eq.{student_id}",
                "select": "*",
                "order": "recorded_at.desc",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_by_student_and_topic(
    student_id: str, topic_id: str
) -> list[dict]:
    """SELECT all performance records for a specific student + topic pair."""
    async with get_client() as client:
        resp = await client.get(
            "/performance_records",
            params={
                "student_id": f"eq.{student_id}",
                "topic_id": f"eq.{topic_id}",
                "select": "*",
                "order": "recorded_at.desc",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_by_id(record_id: str) -> dict | None:
    """SELECT a single performance record by ID."""
    async with get_client() as client:
        resp = await client.get(
            "/performance_records",
            params={"id": f"eq.{record_id}", "select": "*"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
