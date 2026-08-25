from app.core.supabase_client import get_client


async def get_all_topics() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/topics")
        response.raise_for_status()
        return response.json()


async def get_topic_by_id(topic_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/topics", params={"id": f"eq.{topic_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_topics_for_subject(subject_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/topics", params={"subject_id": f"eq.{subject_id}"})
        response.raise_for_status()
        return response.json()


async def create_topic(subject_id: int, name: str, difficulty: int, estimated_hours: float) -> dict:
    async with get_client() as client:
        response = await client.post("/topics", json={
            "subject_id": subject_id, "name": name,
            "difficulty": difficulty, "estimated_hours": estimated_hours
        })
        response.raise_for_status()
        return response.json()[0]
