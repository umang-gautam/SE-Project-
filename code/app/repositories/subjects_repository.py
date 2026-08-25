from app.core.supabase_client import get_client


async def get_all_subjects() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/subjects")
        response.raise_for_status()
        return response.json()


async def get_subject_by_id(subject_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/subjects", params={"id": f"eq.{subject_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def create_subject(code: str, name: str, credits: float, weekly_effort_hours: float) -> dict:
    async with get_client() as client:
        response = await client.post("/subjects", json={
            "code": code, "name": name, "credits": credits, "weekly_effort_hours": weekly_effort_hours
        })
        response.raise_for_status()
        return response.json()[0]
