"""
Shared test fixtures.

The key fixture here is `client` — a FastAPI TestClient that lets us
make HTTP requests to our app without starting a real server.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Synchronous test client for the FastAPI app."""
    return TestClient(app)
