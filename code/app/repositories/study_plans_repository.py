from app.core.supabase_client import get_client


async def get_all_plans() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/study_plans")
        response.raise_for_status()
        return response.json()


async def get_plan_by_id(plan_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/study_plans", params={"id": f"eq.{plan_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_plans_for_student(student_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/study_plans", params={"student_id": f"eq.{student_id}"})
        response.raise_for_status()
        return response.json()


async def create_plan(student_id: int, week_start_date: str, status: str) -> dict:
    async with get_client() as client:
        response = await client.post("/study_plans", json={
            "student_id": student_id, "week_start_date": week_start_date, "status": status
        })
        response.raise_for_status()
        return response.json()[0]
