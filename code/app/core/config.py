import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Student Workload Balancer"
    database_url: str | None = None  # kept for optional direct-DB checks; not used by Supabase REST calls

    supabase_url: str
    supabase_service_key: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()