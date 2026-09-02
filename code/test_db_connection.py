"""Manual check: python test_db_connection.py (needs DATABASE_URL in .env)."""
from sqlalchemy import text

from app.core.database import get_engine

with get_engine().connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print("Connection successful:", result.fetchone())
