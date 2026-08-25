from app.core.supabase_client import get_client


async def get_all_sessions() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/study_sessions")
        response.raise_for_status()
        return response.json()


async def get_session_by_id(session_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/study_sessions", params={"id": f"eq.{session_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_sessions_for_plan(plan_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/study_sessions", params={"study_plan_id": f"eq.{plan_id}"})
        response.raise_for_status()
        return response.json()


async def create_session(study_plan_id: int, topic_id: int, scheduled_start: str,
                          duration_minutes: int, status: str, rebalanced_from_session_id: int | None) -> dict:
    async with get_client() as client:
        response = await client.post("/study_sessions", json={
            "study_plan_id": study_plan_id, "topic_id": topic_id,
            "scheduled_start": scheduled_start, "duration_minutes": duration_minutes,
            "status": status, "rebalanced_from_session_id": rebalanced_from_session_id
        })
        response.raise_for_status()
        return response.json()[0]
