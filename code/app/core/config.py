from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Student Workload Balancer"

settings = Settings()