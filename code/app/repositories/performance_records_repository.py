from app.core.supabase_client import get_client


async def get_all_records() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/performance_records")
        response.raise_for_status()
        return response.json()


async def get_record_by_id(record_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/performance_records", params={"id": f"eq.{record_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_records_for_student(student_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/performance_records", params={"student_id": f"eq.{student_id}"})
        response.raise_for_status()
        return response.json()


async def create_record(student_id: int, topic_id: int, score: float, record_type: str) -> dict:
    async with get_client() as client:
        response = await client.post("/performance_records", json={
            "student_id": student_id, "topic_id": topic_id,
            "score": score, "record_type": record_type
        })
        response.raise_for_status()
        return response.json()[0]
