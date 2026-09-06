import os

# Settings() is constructed at import time and requires these. Point at
# nothing real so no test can accidentally reach Supabase.
os.environ.setdefault("SUPABASE_URL", "http://supabase.invalid")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")
os.environ.pop("DATABASE_URL", None)

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
