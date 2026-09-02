from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_engine
from app.core.supabase_client import get_client

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Liveness plus a best-effort check of each backing service.

    Always returns 200 so a container stays 'up' while a dependency is
    down; consumers read the per-service fields.
    """
    return {
        "status": "ok",
        "database": _database_status(),
        "supabase": await _supabase_status(),
    }


def _database_status() -> str:
    if not settings.database_url:
        return "unconfigured"
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:  # noqa: BLE001 - report, don't crash
        return f"error: {type(exc).__name__}"


async def _supabase_status() -> str:
    try:
        async with get_client() as client:
            response = await client.get("/", timeout=3.0)
        return "ok" if response.status_code < 500 else f"error: HTTP {response.status_code}"
    except Exception as exc:  # noqa: BLE001
        return f"error: {type(exc).__name__}"
