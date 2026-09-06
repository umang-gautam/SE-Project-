"""Route + service layers, with the repository (Supabase) layer replaced."""
from app.repositories import students_repository as repo

ROW = {"id": 1, "name": "Asha", "email": "asha@example.com", "created_at": "2026-09-01T10:00:00Z"}


def test_list_students(client, monkeypatch):
    async def fake_all():
        return [ROW]
    monkeypatch.setattr(repo, "get_all_students", fake_all)
    assert client.get("/students/").json() == [ROW]


def test_get_missing_student_is_404(client, monkeypatch):
    async def fake_one(student_id):
        return None
    monkeypatch.setattr(repo, "get_student_by_id", fake_one)
    assert client.get("/students/99").status_code == 404


def test_create_student_validates_email(client, monkeypatch):
    calls = []

    async def fake_create(name, email):
        calls.append((name, email))
        return ROW
    monkeypatch.setattr(repo, "create_student", fake_create)

    assert client.post("/students/", json={"name": "Asha", "email": "not-an-email"}).status_code == 422
    assert calls == []
    assert client.post("/students/", json={"name": "Asha", "email": "asha@example.com"}).status_code == 201
    assert calls == [("Asha", "asha@example.com")]
