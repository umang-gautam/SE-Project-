"""
Integration tests for the Student CRUD routes.

We mock the service layer (not the repo layer) so we test:
  - HTTP method + path → correct handler
  - Pydantic request validation
  - Response shape and status codes
  - 404 handling when a resource isn't found

This pattern applies to all CRUD entities — we test students
thoroughly as the exemplar and trust the identical pattern
works for the others.
"""

from unittest.mock import AsyncMock, patch

import pytest


# ── Fixtures ──────────────────────────────────────────────────

MOCK_STUDENT = {
    "id": "stu-001",
    "name": "Alice",
    "email": "alice@example.com",
}


# ── POST /students/ ──────────────────────────────────────────

class TestCreateStudent:
    @patch("app.api.routes.students.student_service")
    def test_create_success(self, mock_svc, client):
        mock_svc.create_student = AsyncMock(return_value=MOCK_STUDENT)
        resp = client.post("/students/", json={"name": "Alice", "email": "alice@example.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "stu-001"
        assert data["name"] == "Alice"
        mock_svc.create_student.assert_called_once()

    def test_create_missing_field_returns_422(self, client):
        """Pydantic rejects the request before any service is called."""
        resp = client.post("/students/", json={"name": "Alice"})
        assert resp.status_code == 422


# ── GET /students/ ────────────────────────────────────────────

class TestListStudents:
    @patch("app.api.routes.students.student_service")
    def test_list_returns_array(self, mock_svc, client):
        mock_svc.get_students = AsyncMock(return_value=[MOCK_STUDENT])
        resp = client.get("/students/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) == 1


# ── GET /students/{id} ───────────────────────────────────────

class TestGetStudent:
    @patch("app.api.routes.students.student_service")
    def test_get_found(self, mock_svc, client):
        mock_svc.get_student = AsyncMock(return_value=MOCK_STUDENT)
        resp = client.get("/students/stu-001")
        assert resp.status_code == 200
        assert resp.json()["id"] == "stu-001"

    @patch("app.api.routes.students.student_service")
    def test_get_not_found_returns_404(self, mock_svc, client):
        mock_svc.get_student = AsyncMock(return_value=None)
        resp = client.get("/students/nonexistent")
        assert resp.status_code == 404


# ── PATCH /students/{id} ─────────────────────────────────────

class TestUpdateStudent:
    @patch("app.api.routes.students.student_service")
    def test_update_success(self, mock_svc, client):
        updated = {**MOCK_STUDENT, "name": "Alice Updated"}
        mock_svc.update_student = AsyncMock(return_value=updated)
        resp = client.patch("/students/stu-001", json={"name": "Alice Updated"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice Updated"

    @patch("app.api.routes.students.student_service")
    def test_update_not_found_returns_404(self, mock_svc, client):
        mock_svc.update_student = AsyncMock(return_value=None)
        resp = client.patch("/students/stu-001", json={"name": "Bob"})
        assert resp.status_code == 404


# ── DELETE /students/{id} ────────────────────────────────────

class TestDeleteStudent:
    @patch("app.api.routes.students.student_service")
    def test_delete_success(self, mock_svc, client):
        mock_svc.delete_student = AsyncMock(return_value=True)
        resp = client.delete("/students/stu-001")
        assert resp.status_code == 204

    @patch("app.api.routes.students.student_service")
    def test_delete_not_found_returns_404(self, mock_svc, client):
        mock_svc.delete_student = AsyncMock(return_value=False)
        resp = client.delete("/students/nonexistent")
        assert resp.status_code == 404
