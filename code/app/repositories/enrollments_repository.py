from app.core.supabase_client import get_client


async def get_all_enrollments() -> list[dict]:
    async with get_client() as client:
        response = await client.get("/enrollments")
        response.raise_for_status()
        return response.json()


async def get_enrollment_by_id(enrollment_id: int) -> dict | None:
    async with get_client() as client:
        response = await client.get("/enrollments", params={"id": f"eq.{enrollment_id}"})
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None


async def get_enrollments_for_student(student_id: int) -> list[dict]:
    async with get_client() as client:
        response = await client.get("/enrollments", params={"student_id": f"eq.{student_id}"})
        response.raise_for_status()
        return response.json()


async def create_enrollment(student_id: int, subject_id: int, target_grade: str | None) -> dict:
    async with get_client() as client:
        response = await client.post("/enrollments", json={
            "student_id": student_id, "subject_id": subject_id, "target_grade": target_grade
        })
        response.raise_for_status()
        return response.json()[0]
