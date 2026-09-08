"""
Application configuration via pydantic-settings.

Reads from a .env file (or real environment variables in production).
Every setting is declared once here with its type — if a required value
is missing, the app will refuse to start with a clear error message.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All environment-driven configuration for the backend."""

    # ── Supabase ──────────────────────────────────────────────
    supabase_url: str
    supabase_key: str

    # ── Application ───────────────────────────────────────────
    app_name: str = "Workload Balancer API"
    debug: bool = False

    # ── CORS ──────────────────────────────────────────────────
    # Comma-separated origins allowed to call this API.
    # Default covers the Vite dev server.
    cors_origins: str = "http://localhost:5173"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse the comma-separated CORS string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Singleton — import this everywhere instead of re-reading .env each time.
settings = Settings()
