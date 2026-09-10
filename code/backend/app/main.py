"""
FastAPI application entry point.

Responsibilities (and nothing else):
  - Create the FastAPI app instance
  - Enable CORS so the React frontend can call us
  - Mount all route modules
  - Expose a /health endpoint for liveness checks
  - Register a global exception handler for consistent error responses
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from httpx import HTTPStatusError

from app.core.config import settings
from app.api.routes import (
    students,
    subjects,
    enrollments,
    topics,
    assignments,
    performance,
    study_plans,
    study_sessions,
)


def create_app() -> FastAPI:
    """Application factory — builds and returns a configured FastAPI app."""

    app = FastAPI(title=settings.app_name, docs_url="/docs", redoc_url="/redoc")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Supabase HTTP errors surface as {"status": <code>, "message": <detail>}
    # instead of a 500 with a stack trace.
    @app.exception_handler(HTTPStatusError)
    async def supabase_error_handler(request: Request, exc: HTTPStatusError):
        status_code = exc.response.status_code
        try:
            detail = exc.response.json()
        except Exception:
            detail = exc.response.text
        return JSONResponse(status_code=status_code, content={"status": status_code, "message": detail})

    @app.get("/health")
    async def health_check():
        """Liveness probe — 200 if the server is up."""
        return {"status": "ok"}

    app.include_router(students.router, prefix="/students", tags=["students"])
    app.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
    app.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
    app.include_router(topics.router, prefix="/topics", tags=["topics"])
    app.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
    app.include_router(performance.router, prefix="/performance", tags=["performance"])
    app.include_router(study_plans.router, prefix="/study-plans", tags=["study-plans"])
    app.include_router(study_sessions.router, prefix="/study-sessions", tags=["study-sessions"])

    return app


app = create_app()
