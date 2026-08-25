import httpx  # type: ignore[import-not-found]

from app.core.config import settings

REST_BASE_URL = f"{settings.supabase_url}/rest/v1"

HEADERS = {
    "apikey": settings.supabase_service_key,
    "Authorization": f"Bearer {settings.supabase_service_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=REST_BASE_URL, headers=HEADERS, timeout=10.0)