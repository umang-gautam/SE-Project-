from app.core.supabase_client import get_client


async def get_all_students() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/students")
        response.raise_for_status()
        return response.json()


async def get_student_by_id(student_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/students", params={"id": f"eq.{student_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def create_student(name: str, email: str) -> dict:
    async with get_client() as client:
        response = await client.post("/students", json={"name": name, "email": email})
        response.raise_for_status()
        created = response.json()
        return created[0]