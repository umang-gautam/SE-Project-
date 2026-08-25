from app.core.supabase_client import get_client


async def get_all_assignments() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/assignments")
        response.raise_for_status()
        return response.json()


async def get_assignment_by_id(assignment_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/assignments", params={"id": f"eq.{assignment_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_assignments_for_subject(subject_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/assignments", params={"subject_id": f"eq.{subject_id}"})
        response.raise_for_status()
        return response.json()


async def create_assignment(subject_id: int, title: str, due_date: str, weight: float, status: str) -> dict:
    async with get_client() as client:
        response = await client.post("/assignments", json={
            "subject_id": subject_id, "title": title, "due_date": due_date,
            "weight": weight, "status": status
        })
        response.raise_for_status()
        return response.json()[0]
