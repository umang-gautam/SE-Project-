from app.core import database
from app.core.config import settings


def test_health_reports_unconfigured_db_and_unreachable_supabase(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["database"] == "unconfigured"
    assert body["supabase"].startswith("error:")


def test_unreachable_database_is_reported_not_raised(client, monkeypatch):
    monkeypatch.setattr(settings, "database_url", "postgresql+psycopg2://x:x@127.0.0.1:1/x")
    database.get_engine.cache_clear()
    try:
        body = client.get("/health").json()
    finally:
        database.get_engine.cache_clear()
    assert body["status"] == "ok"
    assert body["database"].startswith("error:")
