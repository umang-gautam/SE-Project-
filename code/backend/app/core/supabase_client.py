"""
Async HTTP client for the Supabase REST API (PostgREST).

Every repository uses this client to talk to Supabase. It handles:
  - Base URL construction (SUPABASE_URL + /rest/v1)
  - Authentication headers (apikey + Bearer token)
  - The "Prefer: return=representation" header so INSERT/UPDATE
    responses include the created/updated row(s)

No business logic lives here — this is pure HTTP plumbing.
"""

import httpx

from app.core.config import settings

# Base URL for all PostgREST calls
_REST_BASE = f"{settings.supabase_url}/rest/v1"

# Headers required by every Supabase REST request
_HEADERS = {
    "apikey": settings.supabase_key,
    "Authorization": f"Bearer {settings.supabase_key}",
    "Content-Type": "application/json",
    # "return=representation" tells PostgREST to send back the
    # row(s) that were inserted/updated/deleted — without it,
    # you'd get an empty 201 and have to make a second query.
    "Prefer": "return=representation",
}


def get_client() -> httpx.AsyncClient:
    """
    Create a fresh async HTTP client pointed at Supabase.

    Usage in a repository:
        async with get_client() as client:
            resp = await client.get("/students", params={"id": "eq.abc"})

    We create a new client per call (short-lived) rather than a global
    singleton because httpx.AsyncClient is lightweight and this avoids
    issues with event-loop lifecycle in async apps.
    """
    return httpx.AsyncClient(
        base_url=_REST_BASE,
        headers=_HEADERS,
        timeout=15.0,
    )
